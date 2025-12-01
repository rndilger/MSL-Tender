"""
Copy all matched images from study subfolders into a single flat folder
for Supabase upload
"""
import os
import shutil
from pathlib import Path

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
photos_dir = os.path.join(project_root, "photos")
staging_dir = os.path.join(project_root, "photos_staged_for_upload")

print("="*80)
print("STAGING IMAGES FOR SUPABASE UPLOAD")
print("="*80)

# Create staging directory
os.makedirs(staging_dir, exist_ok=True)
print(f"Staging directory: {staging_dir}\n")

# Collect all images from photos/ subfolders
images_to_copy = []
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            source_path = os.path.join(root, file)
            images_to_copy.append({
                'source': source_path,
                'filename': file
            })

total = len(images_to_copy)
print(f"Found {total} images to stage")

# Copy images to staging folder
print(f"\nCopying images to staging folder...")
copied_count = 0
errors = []

for img in images_to_copy:
    try:
        dest_path = os.path.join(staging_dir, img['filename'])
        
        # Check for duplicate filenames
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(img['filename'])
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(staging_dir, f"{base}_dup{counter}{ext}")
                counter += 1
        
        shutil.copy2(img['source'], dest_path)
        copied_count += 1
        
        if copied_count % 100 == 0:
            print(f"  Copied {copied_count}/{total}...")
            
    except Exception as e:
        errors.append(f"{img['filename']}: {str(e)}")

print(f"\n✓ Copied {copied_count} images to staging folder")

if errors:
    print(f"\n⚠️ Errors encountered: {len(errors)}")
    for err in errors[:5]:
        print(f"  {err}")

# Verify
staged_files = [f for f in os.listdir(staging_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"\n{'='*80}")
print("VERIFICATION")
print(f"{'='*80}")
print(f"Images copied: {copied_count}")
print(f"Images in staging folder: {len(staged_files)}")

if len(staged_files) == 1490:
    print("\n✅ SUCCESS! All 1,490 images staged for Supabase upload")
    print(f"   Location: {staging_dir}")
else:
    print(f"\n⚠️ Expected 1490 images, found {len(staged_files)}")
