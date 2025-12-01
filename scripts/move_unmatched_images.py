"""
Move images without database records to an archive folder
Keep only images that have matching database records
"""
import pandas as pd
import os
import shutil
from pathlib import Path

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")
archive_dir = os.path.join(project_root, "photos_archive_no_db_record")

print("="*80)
print("MOVING IMAGES WITHOUT DATABASE RECORDS")
print("="*80)

# Create archive directory
os.makedirs(archive_dir, exist_ok=True)
print(f"Archive directory: {archive_dir}")

# Load database
df = pd.read_csv(csv_path)
db_ids = set(df['standardized_chop_id'].dropna())
print(f"\nDatabase records: {len(db_ids)}")

# Scan all images
all_images = []
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            full_path = os.path.join(root, file)
            image_id = Path(file).stem
            all_images.append({
                'path': full_path,
                'filename': file,
                'id': image_id,
                'has_db_record': image_id in db_ids
            })

total_images = len(all_images)
matched_images = sum(1 for img in all_images if img['has_db_record'])
unmatched_images = total_images - matched_images

print(f"Total images found: {total_images}")
print(f"Images WITH DB records: {matched_images}")
print(f"Images WITHOUT DB records: {unmatched_images}")

# Move unmatched images to archive
print(f"\nMoving {unmatched_images} images to archive...")
moved_count = 0
errors = []

for img in all_images:
    if not img['has_db_record']:
        try:
            dest_path = os.path.join(archive_dir, img['filename'])
            # Handle duplicates by adding number
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(img['filename'])
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(archive_dir, f"{base}_dup{counter}{ext}")
                    counter += 1
            
            shutil.move(img['path'], dest_path)
            moved_count += 1
            if moved_count % 50 == 0:
                print(f"  Moved {moved_count}/{unmatched_images}...")
        except Exception as e:
            errors.append(f"{img['filename']}: {str(e)}")

print(f"\n✓ Moved {moved_count} images to archive")

if errors:
    print(f"\n⚠️ Errors encountered: {len(errors)}")
    for err in errors[:5]:
        print(f"  {err}")

# Verify remaining images
remaining_images = []
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            remaining_images.append(file)

print(f"\n{'='*80}")
print("VERIFICATION")
print(f"{'='*80}")
print(f"Images remaining in photos/: {len(remaining_images)}")
print(f"Database records: {len(db_ids)}")
print(f"Images in archive: {moved_count}")

if len(remaining_images) == len(db_ids):
    print("\n✅ SUCCESS! Photos folder now has exactly 1:1 match with database")
    print(f"   {len(remaining_images)} images = {len(db_ids)} database records")
else:
    print(f"\n⚠️ Mismatch: {len(remaining_images)} images vs {len(db_ids)} records")
