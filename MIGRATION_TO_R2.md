# Migration to Cloudflare R2 - Implementation Plan

## Current Situation
- **Problem**: Supabase Storage at 389% of free tier (3.888 GB / 1 GB limit)
- **Images**: 1,490 pork sample images currently in Supabase Storage
- **Impact**: Project is over quota and cannot use Supabase features
- **Growth**: Image library will continue to expand with new studies

## Solution: Migrate to Cloudflare R2
- **Free tier**: 10 GB storage (vs Supabase's 1 GB)
- **Cost after**: $0.015/GB/month (vs Supabase Pro $25/month)
- **No egress fees**: Unlimited image serving at no cost
- **S3-compatible**: Easy to use existing tools and libraries

---

## Phase 1: Cloudflare R2 Setup

### 1.1 Create Cloudflare Account & R2 Bucket
1. Sign up at https://dash.cloudflare.com/sign-up
2. Go to R2 Object Storage → Create bucket
3. Bucket name: `msl-tender-images` (or similar)
4. Location: Automatic (closest to users)
5. Note the bucket endpoint URL

### 1.2 Generate R2 API Credentials
1. R2 → Manage R2 API Tokens → Create API Token
2. Permissions: Object Read & Write
3. Save these securely:
   - `R2_ACCOUNT_ID`: Your Cloudflare account ID
   - `R2_ACCESS_KEY_ID`: API token access key
   - `R2_SECRET_ACCESS_KEY`: API token secret

### 1.3 Configure Public Access
1. Go to bucket settings → Public Access
2. Enable "Allow Access" for public.r2.dev domain
3. Note the public URL: `https://pub-xxxxx.r2.dev/`
4. OR set up custom domain (optional, recommended for production)

---

## Phase 2: Download Images from Supabase

### 2.1 Create Download Script
**Location**: `scripts/download_from_supabase.py`

```python
import os
from supabase import create_client
from pathlib import Path
import requests

# Supabase credentials
SUPABASE_URL = "https://vxqpbohiradglqfxwjco.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"  # Get from Supabase dashboard

# Local download directory
DOWNLOAD_DIR = Path("temp_images_for_migration")
DOWNLOAD_DIR.mkdir(exist_ok=True)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# List all files in the bucket
files = supabase.storage.from_('pork-images').list('original')

print(f"Found {len(files)} files to download")

for i, file in enumerate(files, 1):
    filename = file['name']
    print(f"[{i}/{len(files)}] Downloading {filename}...")
    
    # Get public URL
    public_url = supabase.storage.from_('pork-images').get_public_url(f'original/{filename}')
    
    # Download file
    response = requests.get(public_url)
    
    if response.status_code == 200:
        output_path = DOWNLOAD_DIR / filename
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"  ✓ Saved to {output_path}")
    else:
        print(f"  ✗ Failed to download {filename}: {response.status_code}")

print(f"\nDownload complete! Images saved to {DOWNLOAD_DIR}")
```

### 2.2 Run Download Script
```bash
cd "c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
python scripts/download_from_supabase.py
```

---

## Phase 3: Upload Images to Cloudflare R2

### 3.1 Install Dependencies
```bash
pip install boto3  # S3-compatible client for R2
```

### 3.2 Create Upload Script
**Location**: `scripts/upload_to_r2.py`

```python
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

# R2 credentials (from Phase 1.2)
R2_ACCOUNT_ID = "YOUR_ACCOUNT_ID"
R2_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
R2_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
BUCKET_NAME = "msl-tender-images"

# Local images directory
IMAGES_DIR = Path("temp_images_for_migration")

# Configure S3 client for R2
s3 = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'  # R2 uses 'auto' for region
)

# Upload all images
image_files = list(IMAGES_DIR.glob('*'))
print(f"Found {len(image_files)} images to upload")

for i, image_path in enumerate(image_files, 1):
    filename = image_path.name
    print(f"[{i}/{len(image_files)}] Uploading {filename}...")
    
    try:
        # Upload to R2 with public-read ACL
        s3.upload_file(
            str(image_path),
            BUCKET_NAME,
            f'original/{filename}',
            ExtraArgs={'ContentType': 'image/jpeg'}  # Adjust if you have other formats
        )
        print(f"  ✓ Uploaded {filename}")
    except ClientError as e:
        print(f"  ✗ Failed to upload {filename}: {e}")

print("\nUpload complete!")
```

### 3.3 Run Upload Script
```bash
python scripts/upload_to_r2.py
```

---

## Phase 4: Update Application Code

### 4.1 Update Database Records
The `sample_images` table has a `storage_url` column that currently points to Supabase.

**SQL to update all URLs**:
```sql
-- Update sample_images table to use R2 URLs
UPDATE sample_images
SET storage_url = REPLACE(
  storage_url,
  'https://vxqpbohiradglqfxwjco.supabase.co/storage/v1/object/public/pork-images',
  'https://pub-xxxxx.r2.dev'  -- Replace with your R2 public URL
);

-- Verify the update
SELECT id, original_filename, storage_url 
FROM sample_images 
LIMIT 5;
```

### 4.2 Update Environment Variables in Vercel
1. Vercel Dashboard → Project → Settings → Environment Variables
2. Add new variables:
   - `R2_PUBLIC_URL`: `https://pub-xxxxx.r2.dev` (your R2 public endpoint)
   - Optional: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` (if you need server-side uploads later)
3. Redeploy application

### 4.3 Update Image Upload Code (Future)
When you build the admin interface to upload new images, use R2 instead:

**Example**: `app/lib/r2/client.ts`
```typescript
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'

const r2Client = new S3Client({
  region: 'auto',
  endpoint: `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
})

export async function uploadImageToR2(
  filename: string,
  fileBuffer: Buffer,
  contentType: string = 'image/jpeg'
): Promise<string> {
  await r2Client.send(new PutObjectCommand({
    Bucket: 'msl-tender-images',
    Key: `original/${filename}`,
    Body: fileBuffer,
    ContentType: contentType,
  }))
  
  return `${process.env.R2_PUBLIC_URL}/original/${filename}`
}
```

---

## Phase 5: Cleanup & Verification

### 5.1 Verify R2 Migration
1. Check a few sample images in the app are loading from R2
2. Check browser DevTools → Network tab to confirm R2 URLs
3. Verify database `sample_images.storage_url` all point to R2

### 5.2 Delete Images from Supabase Storage
**ONLY AFTER CONFIRMING R2 WORKS**

1. Supabase Dashboard → Storage → pork-images bucket
2. Select all files in `original/` folder
3. Delete files
4. Verify storage usage drops below 1 GB

### 5.3 Update Documentation
Update `README.md` and `DEPLOYMENT_SUMMARY.md` to reflect:
- Image storage now uses Cloudflare R2
- Remove Supabase Storage setup instructions
- Add R2 setup instructions

---

## Phase 6: Authentication Fix (Resume After Migration)

Once storage is resolved and Supabase is functional again:

### 6.1 Create First Admin User
1. Go to deployed app: `/admin/login`
2. Enter email: `rdilger2@illinois.edu`
3. Click "Send Magic Link" (will fail - expected)
4. Go to Supabase Dashboard → Authentication → Add User
5. Enter email, create user, copy UUID
6. Run SQL:
```sql
INSERT INTO admin_users (id, email, full_name, role, is_active)
VALUES (
  'PASTE-UUID-HERE',
  'rdilger2@illinois.edu',
  'Ryan Dilger',
  'super_admin',
  true
);
```
7. Try login again - magic link should arrive
8. Click link → Dashboard should load with 1,490 samples displayed

---

## Estimated Timeline

- **Phase 1** (R2 Setup): 15 minutes
- **Phase 2** (Download from Supabase): 30-60 minutes (depending on bandwidth)
- **Phase 3** (Upload to R2): 30-60 minutes (depending on bandwidth)
- **Phase 4** (Update App): 15 minutes
- **Phase 5** (Verification & Cleanup): 15 minutes
- **Phase 6** (Authentication): 10 minutes

**Total**: ~2-3 hours

---

## Cost Analysis

### Current (Supabase Storage - OVER QUOTA)
- Storage: 3.888 GB (389% of free tier)
- Status: ⚠️ **BLOCKED** - Cannot use free tier

### After Migration to R2
- **Cloudflare R2**: 3.888 GB / 10 GB free tier = 39% ✅
- **Supabase**: Database only (0.034 GB / 0.5 GB = 7%) ✅
- **Monthly cost**: $0
- **Headroom**: 6.1 GB available for growth

### Future Growth Scenarios
- **10 GB total images**: Still free on R2
- **20 GB total images**: $0.15/month (10 GB over × $0.015/GB)
- **50 GB total images**: $0.60/month (40 GB over × $0.015/GB)

---

## Backup Strategy

After migration, maintain local backups:
```bash
# Periodic backup from R2
python scripts/backup_r2_images.py
```

Store backups in `photos_backup/` (already in .gitignore)

---

## Next Session Checklist

When you resume:
- [ ] Phase 1: Set up Cloudflare R2 account and bucket
- [ ] Phase 2: Download 1,490 images from Supabase to local temp folder
- [ ] Phase 3: Upload images to R2
- [ ] Phase 4: Update database URLs and environment variables
- [ ] Phase 5: Verify images load, delete from Supabase
- [ ] Phase 6: Create first admin user and test authentication

---

## Questions to Address Next Session

1. Custom domain for R2? (e.g., `images.msl-tender.com` instead of `pub-xxxxx.r2.dev`)
2. Image optimization pipeline? (resize/compress on upload)
3. Backup schedule? (weekly/monthly automated backups)
4. Future image upload workflow? (admin interface design)

---

**Status**: Ready to begin Phase 1
**Last Updated**: November 30, 2025
**Contact**: Resume with "Let's continue the R2 migration"
