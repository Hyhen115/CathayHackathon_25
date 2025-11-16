import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
import os

class s3_uploader:
    def __init__(self):
        self.s3_client = self.get_s3_client()

    def get_s3_client(self):
        try:
            s3_client = boto3.client(
                's3',
            )
            return s3_client
        except Exception as e:
            print(f"Error initializing S3 client: {str(e)}")
            return None
    
    def upload_to_s3(self, imgpath, bucket_name):
        if not self.s3_client:
            return None
        
        try:
            filename = os.path.basename(imgpath)
            with open(imgpath, "rb") as file:
                self.s3_client.upload_fileobj(
                    file,
                    bucket_name,
                    filename,
                    ExtraArgs={"ContentType": "image/png"}
                )
            # Generate URL
            url = f"https://{bucket_name}.s3.ap-northeast-1.amazonaws.com/{filename}.png"
            print(f"Uploaded to S3: {url}")
            return url
        
        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
        

