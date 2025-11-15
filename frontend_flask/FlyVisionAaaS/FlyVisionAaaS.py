from .components.screenshot import ScreenCapturer
from .components.s3_uploader import s3_uploader
import os
from dotenv import load_dotenv
import requests

class FlyVisionAaaS:
    def __init__(self):
        load_dotenv()
        self.screen_capturer = ScreenCapturer()
        self.s3_uploader = s3_uploader()
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.backend_url = os.getenv("BACKEND_URL")

    def recognize_image(self):
        img = self.screen_capturer.screenshot_full()
        url = self.s3_uploader.upload_to_s3(img, self.bucket_name)

        payload = {
                    "image_s3_url": url,
                    "touch_point": {
                        "x": 540,
                        "y": 960
                    },
                    "screen_resolution": {
                        "width": 1080,
                        "height": 1920
                    }
                }
        response = requests.post(f"{self.backend_url}/api/recommend", json=payload)
        if response.ok:
            try:
                result = response.json()
                print(f"Response JSON: {str(result)}")
                if result.get("label") is not None:
                    url=result.get("label")
                return url
            except Exception as e:
                print(f"Error parsing JSON response: {str(e)}")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None


