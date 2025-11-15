import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="IFE",
    page_icon="",
    layout="centered"
)

# Initialize S3 client
def get_s3_client():
    """Initialize and return S3 client"""
    try:
        s3_client = boto3.client(
            's3',
        )
        return s3_client
    except Exception as e:
        st.error(f"Error initializing S3 client: {str(e)}")
        return None

def upload_to_s3(file, bucket_name):
    """
    Upload file to S3 bucket and return the URL
    
    Args:
        file: Uploaded file object from Streamlit
        bucket_name: Name of the S3 bucket
    
    Returns:
        str: URL of the uploaded file or None if upload failed
    """
    s3_client = get_s3_client()
    
    if not s3_client:
        return None
    
    try:
        # Generate unique filename
        file_extension = file.name.split('.')[-1]
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            unique_filename,
            ExtraArgs={'ContentType': file.type}
        )
        
        # Generate URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
        
        return url
    
    except ClientError as e:
        st.error(f"Error uploading to S3: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def main():
    # Header
    st.title("📸 Image Upload to S3")
    st.markdown("Upload an image file to AWS S3 bucket and get the URL")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        bucket_name = st.text_input(
            "S3 Bucket Name",
            value=os.getenv('S3_BUCKET_NAME', ''),
            help="Enter your S3 bucket name"
        )
        
        st.markdown("---")
        st.markdown("### 🔑 Required Environment Variables")
        st.markdown("""
        - `AWS_ACCESS_KEY_ID`
        - `AWS_SECRET_ACCESS_KEY`
        - `AWS_REGION` (optional, defaults to us-east-1)
        - `S3_BUCKET_NAME` (optional)
        """)
    
    # Main content
    if not bucket_name:
        st.warning("⚠️ Please enter your S3 bucket name in the sidebar")
        return
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="Select an image file to upload to S3"
    )
    
    # Display uploaded image
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Image", use_container_width=True)
        
        st.markdown("---")
        
        # Upload button
        if st.button("🚀 Upload to S3", type="primary", use_container_width=True):
            with st.spinner("Uploading to S3..."):
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                
                # Upload to S3
                url = upload_to_s3(uploaded_file, bucket_name)
                
                if url:
                    st.success("✅ Upload successful!")
                    st.markdown("### 🔗 Image URL")
                    st.code(url, language=None)
                    
                    # Copy button functionality
                    st.markdown(
                        f"""
                        <a href="{url}" target="_blank">
                            <button style="
                                background-color: #0066cc;
                                color: white;
                                padding: 10px 20px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                            ">
                                Open Image in New Tab
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error("❌ Upload failed. Please check your AWS credentials and bucket name.")

if __name__ == "__main__":
    main()
