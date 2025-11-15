# Product Recommendation API

Django backend service that uses AWS Rekognition to detect objects in images and recommend products based on user touch interactions.

## Features

- Image object detection using AWS Rekognition
- Touch point analysis to identify user-selected objects
- Product recommendation based on detected labels
- S3 integration for image storage and product mapping

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- AWS account with Rekognition and S3 access
- Valid AWS credentials

## Setup

### 1. Install Dependencies

Dependencies are managed via `uv` and will be installed automatically when running commands.

### 2. Configure Environment Variables

Copy the example environment file and update with your AWS credentials:

```bash
cp .env.example .env
```

Edit `.env` and set your AWS credentials:

```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=your-session-token  # if using temporary credentials
AWS_REGION=ap-southeast-1

PRODUCT_INDEX_BUCKET=your-product-index-bucket
PRODUCT_INDEX_PREFIX=product-index
```

**Note**: Load these environment variables before running the server:

```bash
export $(cat .env | xargs)
```

Or use `python-dotenv` by adding it to dependencies and loading in `settings.py`.

### 3. Run Database Migrations

```bash
uv run python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
uv run python manage.py createsuperuser
```

### 5. Start the Development Server

```bash
uv run python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`

To make it accessible from other devices:

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

## API Documentation

### Endpoint: Product Recommendation

**URL**: `/api/recommend`

**Method**: `POST`

**Content-Type**: `application/json`

#### Request Body

```json
{
  "image_s3_url": "https://your-bucket.s3.ap-southeast-1.amazonaws.com/path/to/image.jpg",
  "touch_point": {
    "x": 540,
    "y": 960
  },
  "screen_resolution": {
    "width": 1080,
    "height": 1920
  }
}
```

**Parameters**:

- `image_s3_url` (string, required): S3 URL of the image. Supports:
  - `s3://bucket/key`
  - `https://bucket.s3.region.amazonaws.com/key`
  - `https://s3.region.amazonaws.com/bucket/key`
  
- `touch_point` (object, required): User's touch coordinates
  - `x` (number): Horizontal pixel position
  - `y` (number): Vertical pixel position

- `screen_resolution` (object, required): Screen dimensions
  - `width` (number): Screen width in pixels
  - `height` (number): Screen height in pixels

#### Success Response

**Code**: `200 OK`

```json
{
  "product_url": "https://example.com/product/123"
}
```

#### Error Responses

**Code**: `400 Bad Request`

```json
{
  "detail": "image_s3_url is required"
}
```

**Code**: `404 Not Found`

```json
{
  "detail": "No product mapping for label: Mobile Phone"
}
```

**Code**: `502 Bad Gateway`

```json
{
  "detail": "Rekognition error: ..."
}
```

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "image_s3_url": "s3://my-bucket/images/photo.jpg",
    "touch_point": {"x": 540, "y": 960},
    "screen_resolution": {"width": 1080, "height": 1920}
  }'
```

## Product Index Setup

The API looks up product URLs from S3 based on detected labels. Store product mappings in your S3 bucket:

### Bucket Structure

```
s3://your-product-index-bucket/
  product-index/
    mobile-phone.json
    laptop.json
    watch.txt
    ...
```

### File Formats

**JSON format** (recommended):

```json
{
  "url": "https://example.com/product/123"
}
```

**Text format**:

```
https://example.com/product/123
```

### Lookup Logic

For a detected label like "Mobile Phone", the API tries these keys in order:

1. `product-index/Mobile Phone.json`
2. `product-index/Mobile Phone.txt`
3. `product-index/mobile phone.json`
4. `product-index/mobile phone.txt`
5. `product-index/mobile-phone.json`
6. `product-index/mobile-phone.txt`

## Configuration

Environment variables for tuning:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | - | AWS region for Rekognition and S3 |
| `REKOGNITION_MAX_LABELS` | 50 | Maximum labels to detect |
| `DETECT_MIN_CONFIDENCE` | 50 | Minimum confidence threshold (0-100) |
| `PRODUCT_INDEX_BUCKET` | - | S3 bucket containing product mappings |
| `PRODUCT_INDEX_PREFIX` | product-index | S3 prefix for product files |
| `S3_TIMEOUT_SECONDS` | 15 | HTTP timeout for image downloads |

## How It Works

1. **Image Fetch**: Downloads image from S3 URL
2. **Object Detection**: Sends image to AWS Rekognition's DetectLabels API
3. **Label Selection**: Analyzes bounding boxes to find the label nearest to the touch point:
   - Prioritizes labels with bounding boxes containing the touch point
   - Falls back to closest label by distance from touch point
4. **Product Lookup**: Queries S3 for product URL using the selected label
5. **Response**: Returns the product URL

## Development

### Project Structure

```
saas/
├── manage.py
├── pyproject.toml
├── backend/
│   ├── settings.py
│   ├── urls.py
│   └── api/
│       ├── __init__.py
│       ├── urls.py
│       └── views.py
```

### Running Tests

```bash
uv run python manage.py test
```

### Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/` with your superuser credentials.

## License

See LICENSE file for details.
