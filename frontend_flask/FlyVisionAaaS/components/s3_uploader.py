import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import uuid

class s3_uploader:
    def __init__(self):
        self.s3_client = self.get_s3_client()

    def get_s3_client():
        try:
            s3_client = boto3.client(
                's3',
            )
            return s3_client
        except Exception as e:
            print(f"Error initializing S3 client: {str(e)}")
            return None
    
    def upload_to_s3(self, file, bucket_name):
        if not self.s3_client:
            return None
        
        try:
            # Generate unique filename
            file_extension = file.name.split('.')[-1]
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file,
                bucket_name,
                unique_filename,
                ExtraArgs={'ContentType': file.type}
            )
            
            # Generate URL
            url = f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
            
            return url
        
        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
        

