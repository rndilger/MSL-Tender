"""
Check how many images are currently in the R2 bucket
"""
import boto3
from botocore.exceptions import ClientError
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# R2 Configuration from environment
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "msl-tender-images")

def count_r2_images():
    """Count objects in R2 bucket"""
    
    # Validate configuration
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("❌ Error: Missing R2 credentials")
        print("   Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
        print("   Create a .env file (see .env.example) or set environment variables")
        sys.exit(1)
    
    print("🔧 Connecting to R2...")
    s3 = boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    
    try:
        # List all objects with prefix 'original/'
        print(f"📊 Counting objects in bucket '{BUCKET_NAME}'...")
        
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=BUCKET_NAME, Prefix='original/')
        
        total_count = 0
        total_size = 0
        
        for page in page_iterator:
            if 'Contents' in page:
                total_count += len(page['Contents'])
                total_size += sum(obj['Size'] for obj in page['Contents'])
        
        print()
        print("=" * 60)
        print(f"📁 R2 Bucket Summary:")
        print(f"   Total images: {total_count}")
        print(f"   Total size: {total_size / (1024*1024):.2f} MB")
        print()
        
        if total_count == 1490:
            print("✅ Expected count (1,490 images) - no duplicates!")
        elif total_count > 1490:
            print(f"⚠️  Warning: {total_count - 1490} extra files detected (possible duplicates)")
        else:
            print(f"⚠️  Warning: {1490 - total_count} images missing")
        
        print("=" * 60)
        
    except ClientError as e:
        print(f"❌ Error accessing R2: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        count_r2_images()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
