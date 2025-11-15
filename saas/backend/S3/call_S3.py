from S3 import S3Uploader

def main():
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