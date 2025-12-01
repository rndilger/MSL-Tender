"""
Quick validation check - verify all DB records have images
"""
import pandas as pd
import os
from pathlib import Path

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")

print("QUICK VALIDATION CHECK")
print("="*60)

# Load data
df = pd.read_csv(csv_path)
print(f"Database records: {len(df)}")

# Get all images quickly
image_ids = set()
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_ids.add(Path(file).stem)

print(f"Total images: {len(image_ids)}")

# Check match
db_ids = set(df['standardized_chop_id'].dropna())
matched = db_ids.intersection(image_ids)
db_only = db_ids - image_ids

print(f"\nMatched: {len(matched)}")
print(f"DB records without images: {len(db_only)}")

if len(db_only) == 0:
    print("\n✅ SUCCESS! All database records have matching images!")
    print(f"   Match rate: {len(matched)}/{len(db_ids)} = 100%")
else:
    print(f"\n⚠️ Found {len(db_only)} records without images:")
    for study in sorted(set(df[df['standardized_chop_id'].isin(db_only)]['study_number'])):
        count = len(df[(df['study_number'] == study) & df['standardized_chop_id'].isin(db_only)])
        print(f"   Study {study}: {count} records")

images_only = image_ids - db_ids
print(f"\nImages without DB records: {len(images_only)}")
print("(These are OK - photos exist for potential future use)")
