import sys
import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

# load backend/.env (two levels up from this file)
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# Try imports that work when run as a module from the project root (preferred)
try:
    from backend.S3.S3 import S3Uploader
except Exception:
    # Fallback to local import if you run this file directly (not recommended)
    try:
        from S3 import S3Uploader
    except Exception as e:
        print("Failed to import S3Uploader:", e)
        raise

def main():
    # Check for available AWS credentials (env, shared config, or IAM role)
    creds = boto3.Session().get_credentials()
    if creds is None or creds.access_key is None:
        print("No AWS credentials detected.")
        print("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, or configure ~/.aws/credentials, or use an IAM role.")
        return

    uploader = S3Uploader()
    demo_file = "backend/S3/demo.jpeg"
    bucket_name = "ifer-s3-demo-bucket"
    object_name = None

    success = uploader.upload_file(demo_file, bucket_name, object_name)
    if success:
        print(f"File '{demo_file}' uploaded successfully to bucket '{bucket_name}'.")
    else:
        print(f"Failed to upload file '{demo_file}' to bucket '{bucket_name}'.")

if __name__ == "__main__":
    main()