import os
from dotenv import load_dotenv
import boto3
import logging
from botocore.exceptions import ClientError

# Load .env file from the backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class S3Uploader:
    def __init__(self):
        """Initialize the S3Uploader with AWS credentials."""
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        print ("self.aws_access_key_id:", self.aws_access_key_id)
        print ("self.aws_secret_access_key:", self.aws_secret_access_key)

    def upload_file(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket.

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)
        try:
            response = self.s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True