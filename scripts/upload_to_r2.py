"""
Upload pork sample images from local directory to Cloudflare R2
"""
import boto3
from pathlib import Path
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
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# Local images directory
IMAGES_DIR = Path("photos_staged_for_upload")

def upload_images_to_r2():
    """Upload all images from local folder to R2"""
    
    # Validate configuration
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL]):
        print("❌ Error: Missing R2 credentials")
        print("   Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL")
        print("   Create a .env file (see .env.example) or set environment variables")
        sys.exit(1)
    
    if not IMAGES_DIR.exists():
        print(f"❌ Error: Directory not found: {IMAGES_DIR}")
        print(f"   Current directory: {Path.cwd()}")
        sys.exit(1)
    
    # Configure S3 client for R2
    print("🔧 Configuring R2 client...")
    s3 = boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    
    # Get list of images (case-insensitive using rglob with a set to deduplicate)
    image_files = []
    seen_files = set()
    for pattern in ['*.JPG', '*.JPEG', '*.jpg', '*.jpeg']:
        for file in IMAGES_DIR.glob(pattern):
            if file.name.lower() not in seen_files:
                seen_files.add(file.name.lower())
                image_files.append(file)
    
    if not image_files:
        print(f"❌ Error: No image files found in {IMAGES_DIR}")
        sys.exit(1)
    
    print(f"📁 Found {len(image_files)} images to upload")
    print(f"📍 Uploading to bucket: {BUCKET_NAME}")
    print(f"🌍 Images will be accessible at: {R2_PUBLIC_URL}/original/[filename]")
    print()
    
    # Upload all images
    uploaded = 0
    failed = 0
    
    for i, image_path in enumerate(image_files, 1):
        filename = image_path.name
        
        # Progress indicator every 50 files
        if i % 50 == 0 or i == 1:
            print(f"[{i}/{len(image_files)}] Uploading {filename}...")
        
        try:
            # Determine content type
            content_type = 'image/jpeg'
            if filename.lower().endswith('.png'):
                content_type = 'image/png'
            
            # Upload to R2
            s3.upload_file(
                str(image_path),
                BUCKET_NAME,
                f'original/{filename}',
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000'  # Cache for 1 year
                }
            )
            uploaded += 1
            
        except ClientError as e:
            print(f"  ✗ Failed to upload {filename}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Unexpected error with {filename}: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"✅ Upload complete!")
    print(f"   Uploaded: {uploaded}/{len(image_files)}")
    if failed > 0:
        print(f"   Failed: {failed}")
    print()
    print(f"🔗 Images are now accessible at:")
    print(f"   {R2_PUBLIC_URL}/original/[filename]")
    print()
    print("📝 Next step: Update database URLs to point to R2")
    print("=" * 60)

if __name__ == "__main__":
    try:
        upload_images_to_r2()
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
