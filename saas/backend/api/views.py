import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import boto3
import requests
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def _parse_s3_url(url: str) -> Optional[Tuple[str, str]]:
    # Supports s3://bucket/key or https://s3.amazonaws.com/bucket/key or virtual-hosted-style
    if url.startswith("s3://"):
        without_scheme = url[len("s3://"):]
        parts = without_scheme.split("/", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return None
    # virtual-hosted-style: https://<bucket>.s3.<region>.amazonaws.com/<key>
    vh = re.match(r"https?://([a-z0-9-_.]+)\.s3[.-][a-z0-9-]+\.amazonaws\.com/(.+)", url)
    if vh:
        return vh.group(1), vh.group(2)
    # path-style: https://s3.<region>.amazonaws.com/<bucket>/<key>
    ps = re.match(r"https?://s3[.-][a-z0-9-]+\.amazonaws\.com/([^/]+)/(.+)", url)
    if ps:
        return ps.group(1), ps.group(2)
    return None


def _fetch_image_bytes(image_url: str, s3_client) -> bytes:
    parsed = _parse_s3_url(image_url)
    if parsed:
        bucket, key = parsed
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read()
    # Assume HTTP(S)
    timeout = float(os.getenv('S3_TIMEOUT_SECONDS', '15'))
    resp = requests.get(image_url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def _normalize_point(point: Dict[str, Any], resolution: Dict[str, Any]) -> Tuple[float, float]:
    sx = float(resolution.get('width'))
    sy = float(resolution.get('height'))
    if sx <= 0 or sy <= 0:
        raise ValueError('Invalid screen resolution')
    x = float(point.get('x'))
    y = float(point.get('y'))
    return x / sx, y / sy


def _best_label_near_point(labels: List[Dict[str, Any]], u: float, v: float) -> Optional[str]:
    best: Optional[Tuple[float, str]] = None  # (score, label)

    # Prefer boxes containing the point; tie-break by smallest area and highest confidence
    containing: List[Tuple[float, float, float, str]] = []  # (area, -confidence, distance, label)

    for label in labels:
        name = label.get('Name')
        instances = label.get('Instances') or []
        for inst in instances:
            box = inst.get('BoundingBox') or {}
            left = float(box.get('Left', 0))
            top = float(box.get('Top', 0))
            width = float(box.get('Width', 0))
            height = float(box.get('Height', 0))
            if width <= 0 or height <= 0:
                continue
            cx = left + width / 2.0
            cy = top + height / 2.0
            inside = (left <= u <= left + width) and (top <= v <= top + height)
            area = width * height
            conf = float(inst.get('Confidence', label.get('Confidence', 0.0)))
            dist2 = (u - cx) ** 2 + (v - cy) ** 2
            if inside:
                containing.append((area, -conf, dist2, name))
            else:
                # score by negative distance and confidence
                score = -dist2 + (conf / 1000.0)
                if best is None or score > best[0]:
                    best = (score, name)

    if containing:
        containing.sort(key=lambda t: (t[0], t[1], t[2]))
        return containing[0][3]

    if best is not None:
        return best[1]

    # Fallback: top label by confidence when no instances present
    if labels:
        labels_sorted = sorted(labels, key=lambda l: float(l.get('Confidence', 0.0)), reverse=True)
        return labels_sorted[0].get('Name')

    return None


def _lookup_product_url_for_label(label: str, s3_client) -> Optional[str]:
    bucket = os.getenv('PRODUCT_INDEX_BUCKET')
    prefix = os.getenv('PRODUCT_INDEX_PREFIX', 'product-index')
    if not bucket:
        return None

    def try_key(key: str) -> Optional[str]:
        try:
            obj = s3_client.get_object(Bucket=bucket, Key=key)
        except s3_client.exceptions.NoSuchKey:  # type: ignore[attr-defined]
            return None
        content = obj['Body'].read()
        # Try JSON
        try:
            data = json.loads(content.decode('utf-8'))
            url = data.get('url')
            if isinstance(url, str) and url.strip():
                return url.strip()
        except Exception:
            pass
        # Fallback to plain text
        txt = content.decode('utf-8').strip()
        return txt if txt else None

    # Normalize label for key variants
    raw = label
    lower = raw.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower).strip('-')

    candidates = [
        f"{prefix}/{raw}.json",
        f"{prefix}/{raw}.txt",
        f"{prefix}/{lower}.json",
        f"{prefix}/{lower}.txt",
        f"{prefix}/{slug}.json",
        f"{prefix}/{slug}.txt",
    ]
    for key in candidates:
        url = try_key(key)
        if url:
            return url
    return None


@csrf_exempt
def recommend_product(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    image_url = payload.get('image_s3_url')
    point = payload.get('touch_point') or {}
    resolution = payload.get('screen_resolution') or {}

    if not isinstance(image_url, str) or not image_url:
        return JsonResponse({'detail': 'image_s3_url is required'}, status=400)
    if not (isinstance(point, dict) and 'x' in point and 'y' in point):
        return JsonResponse({'detail': 'touch_point with x,y required'}, status=400)
    if not (isinstance(resolution, dict) and 'width' in resolution and 'height' in resolution):
        return JsonResponse({'detail': 'screen_resolution with width,height required'}, status=400)

    try:
        s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
        image_bytes = _fetch_image_bytes(image_url, s3_client)
    except Exception as e:
        return JsonResponse({'detail': f'Failed to fetch image: {str(e)}'}, status=400)

    try:
        rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION'))
        max_labels = int(os.getenv('REKOGNITION_MAX_LABELS', '50'))
        min_conf = float(os.getenv('DETECT_MIN_CONFIDENCE', '50'))
        resp = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=max_labels,
            MinConfidence=min_conf,
        )
    except Exception as e:
        return JsonResponse({'detail': f'Rekognition error: {str(e)}'}, status=502)

    labels = resp.get('Labels') or []
    # return JsonResponse({'labels': labels})

    try:
        u, v = _normalize_point(point, resolution)
    except Exception as e:
        return JsonResponse({'detail': f'Invalid touch point or resolution: {str(e)}'}, status=400)
    

    # label_name = _best_label_near_point(labels, u, v)
    # if not label_name:
    #     return JsonResponse({'detail': 'No suitable label found near point'}, status=404)

    # try:
    #     url = _lookup_product_url_for_label(label_name, s3_client)
    # except Exception as e:
    #     return JsonResponse({'detail': f'S3 lookup error: {str(e)}'}, status=502)

    # if not url:
    #     return JsonResponse({'detail': f'No product mapping for label: {label_name}'}, status=404)

    # return JsonResponse({'product_url': url})


@csrf_exempt
def fetch_image(request: HttpRequest):
    """
    Fetch and return image bytes from S3 or HTTP(S) URL.
    
    POST /api/fetch-image
    Body: {"image_url": "s3://bucket/key or https://..."}
    Returns: Raw image bytes with appropriate Content-Type
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    image_url = payload.get('image_url')
    if not isinstance(image_url, str) or not image_url:
        return JsonResponse({'detail': 'image_url is required'}, status=400)

    try:
        s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
        image_bytes = _fetch_image_bytes(image_url, s3_client)
    except Exception as e:
        return JsonResponse({'detail': f'Failed to fetch image: {str(e)}'}, status=400)

    # Determine content type from URL extension
    content_type = 'image/jpeg'
    lower_url = image_url.lower()
    if lower_url.endswith('.png'):
        content_type = 'image/png'
    elif lower_url.endswith('.gif'):
        content_type = 'image/gif'
    elif lower_url.endswith('.webp'):
        content_type = 'image/webp'
    elif lower_url.endswith('.bmp'):
        content_type = 'image/bmp'

    return HttpResponse(image_bytes, content_type=content_type)


@csrf_exempt
def detect_labels(request: HttpRequest):
    """
    Run AWS Rekognition DetectLabels on an image URL.
    
    POST /api/detect-labels
    Body: {"image_url": "s3://bucket/key or https://..."}
    Returns: Full Rekognition DetectLabels response
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    image_url = payload.get('image_url')
    if not isinstance(image_url, str) or not image_url:
        return JsonResponse({'detail': 'image_url is required'}, status=400)

    try:
        s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
        image_bytes = _fetch_image_bytes(image_url, s3_client)
    except Exception as e:
        return JsonResponse({'detail': f'Failed to fetch image: {str(e)}'}, status=400)

    try:
        rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION'))
        max_labels = int(os.getenv('REKOGNITION_MAX_LABELS', '50'))
        min_conf = float(os.getenv('DETECT_MIN_CONFIDENCE', '50'))
        resp = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=max_labels,
            MinConfidence=min_conf,
        )
    except Exception as e:
        return JsonResponse({'detail': f'Rekognition error: {str(e)}'}, status=502)

    return JsonResponse(resp)
