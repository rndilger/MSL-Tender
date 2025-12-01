"""
Detailed investigation of Study 2006 mismatches
"""
import pandas as pd
import os
from pathlib import Path

# Paths
project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")

print("="*80)
print("STUDY 2006 DETAILED INVESTIGATION")
print("="*80)

# Load database
df = pd.read_csv(csv_path)
study_2006 = df[df['study_number'] == 2006].copy()

print(f"\nDatabase records for Study 2006: {len(study_2006)}")
print(f"\nBlock distribution in database:")
print(study_2006['block'].value_counts().sort_index())

print(f"\nSample of database chop IDs:")
print(study_2006['standardized_chop_id'].head(20).tolist())

# Scan for 2006 images
print("\n" + "="*80)
print("IMAGE FILES FOR STUDY 2006")
print("="*80)

image_files = []
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            if file.startswith('2006'):
                full_path = os.path.join(root, file)
                folder = os.path.basename(root)
                filename_base = Path(file).stem
                
                # Extract block from filename (position 5-6 after "2006B")
                if len(filename_base) >= 7:
                    block_str = filename_base[5:7]
                    image_files.append({
                        'filename': file,
                        'filename_base': filename_base,
                        'folder': folder,
                        'block': block_str,
                        'full_path': full_path
                    })

images_df = pd.DataFrame(image_files)

print(f"\nTotal image files for 2006: {len(images_df)}")
print(f"\nBlock distribution in images:")
print(images_df['block'].value_counts().sort_index())

print(f"\nFolders containing 2006 images:")
print(images_df['folder'].value_counts())

print(f"\nSample of image filenames:")
print(images_df['filename_base'].head(20).tolist())

# Compare database IDs with image IDs
print("\n" + "="*80)
print("MATCHING ANALYSIS")
print("="*80)

db_ids = set(study_2006['standardized_chop_id'].dropna())
image_ids = set(images_df['filename_base'])

matched = db_ids.intersection(image_ids)
db_only = db_ids - image_ids
images_only = image_ids - db_ids

print(f"\nMatched: {len(matched)}")
print(f"DB only (no image): {len(db_only)}")
print(f"Images only (no DB): {len(images_only)}")

# Show DB records by block that have no image
print("\n" + "="*80)
print("DB RECORDS WITHOUT IMAGES (by block)")
print("="*80)

db_missing = study_2006[study_2006['standardized_chop_id'].isin(db_only)]
print(f"\nTotal: {len(db_missing)}")
print("\nBlock distribution:")
print(db_missing['block'].value_counts().sort_index())
print("\nSample IDs without images:")
print(db_missing['standardized_chop_id'].head(10).tolist())

# Show images by block that have no DB record
print("\n" + "="*80)
print("IMAGES WITHOUT DB RECORDS (by block)")
print("="*80)

images_missing = images_df[images_df['filename_base'].isin(images_only)]
print(f"\nTotal: {len(images_missing)}")
print("\nBlock distribution:")
print(images_missing['block'].value_counts().sort_index())
print("\nSample filenames without DB:")
print(images_missing['filename_base'].head(10).tolist())

# Check if DB has Block 2 data at all
print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

has_block_2_in_db = (study_2006['block'] == 2).any()
has_block_2_in_images = (images_df['block'] == '02').any()

print(f"\nDatabase has Block 2 records: {has_block_2_in_db}")
print(f"Images have Block 2 files: {has_block_2_in_images}")

if not has_block_2_in_db and has_block_2_in_images:
    print("\n⚠ ISSUE IDENTIFIED:")
    print("  - Database does NOT contain Block 2 data")
    print("  - Images folder DOES contain Block 2 photos")
    print("  - This explains the 67 unmatched images")
    print("\nRECOMMENDATION:")
    print("  1. Search for original Study 2006 Block 2 Excel data")
    print("  2. If found, add to consolidated dataset")
    print("  3. If not found, these 67 images cannot be used in experiments")
