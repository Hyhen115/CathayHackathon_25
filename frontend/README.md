# Image Upload to S3 - Streamlit App

A Streamlit application that allows users to upload images to AWS S3 and get the URL.

## Features

- 📸 Image file selection with preview
- ☁️ Upload to AWS S3 bucket
- 🔗 Get public URL of uploaded image
- 🎨 Clean and intuitive UI
- ⚙️ Configurable bucket settings

## Prerequisites

- Python 3.9 or higher
- AWS account with S3 bucket
- AWS credentials (Access Key ID and Secret Access Key)

## Installation

This project uses `uv` for dependency management. If you don't have `uv` installed:

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Setup Project

1. Clone or navigate to the project directory:
```bash
cd "/Applications/Cathay Hackathon"
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
uv pip install -e .
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit `.env` and add your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

## Usage

1. Activate the virtual environment (if not already activated):
```bash
source .venv/bin/activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser to the URL shown (typically `http://localhost:8501`)

4. In the app:
   - Enter your S3 bucket name in the sidebar (or set it in `.env`)
   - Click "Browse files" to select an image
   - Preview the selected image
   - Click "Upload to S3" to upload
   - Copy the generated URL

## AWS S3 Setup

### Create S3 Bucket

1. Go to AWS S3 Console
2. Click "Create bucket"
3. Choose a unique bucket name
4. Select your region
5. Configure bucket settings (public access if needed)

### Bucket Permissions

If you want uploaded images to be publicly accessible, add this bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### IAM User Permissions

Ensure your IAM user has these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── pyproject.toml      # UV project configuration
├── .env.example        # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Troubleshooting

### Upload fails with "Access Denied"
- Check your AWS credentials are correct
- Verify your IAM user has S3 permissions
- Ensure bucket name is correct

### Images not accessible via URL
- Check bucket permissions
- Make sure bucket policy allows public read access
- Verify the bucket is not blocking public access

### Module not found errors
- Make sure virtual environment is activated
- Run `uv pip install -e .` to install dependencies

## Development

To add new dependencies:

```bash
uv pip install package-name
uv pip freeze > requirements.txt  # Optional
```

## License

MIT License
