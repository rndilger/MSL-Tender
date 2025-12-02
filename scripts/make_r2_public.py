"""
Configure R2 bucket for public read access
"""
import boto3
import json
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

def make_bucket_public():
    """Set bucket policy to allow public read access"""
    
    # Validate configuration
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("❌ Error: Missing R2 credentials")
        print("   Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY in .env file")
        sys.exit(1)
    
    print("🔧 Connecting to R2...")
    s3 = boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    
    # Public read policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicRead",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            }
        ]
    }
    
    try:
        print(f"📝 Setting public read policy on bucket '{BUCKET_NAME}'...")
        s3.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(policy)
        )
        
        print()
        print("=" * 60)
        print("✅ Bucket is now publicly readable!")
        print(f"   All objects in '{BUCKET_NAME}' can be accessed via public URLs")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error setting bucket policy: {e}")
        print()
        print("⚠️  Alternative: Configure public access in Cloudflare Dashboard:")
        print("   1. Go to R2 → Select your bucket")
        print("   2. Settings → Public Access")
        print("   3. Enable 'Allow Access' or configure custom domain")
        sys.exit(1)

if __name__ == "__main__":
    try:
        make_bucket_public()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
