"""
Remove Study 2006 database records that don't have matching images
Keep only the 9 records that have both data and images
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# Paths
project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")

print("="*80)
print("CLEANING STUDY 2006: REMOVE RECORDS WITHOUT IMAGES")
print("="*80)

# Load database
df = pd.read_csv(csv_path)
initial_count = len(df)
study_2006_initial = len(df[df['study_number'] == 2006])

print(f"\nInitial total records: {initial_count}")
print(f"Initial Study 2006 records: {study_2006_initial}")

# Get list of image chop IDs for Study 2006
photos_dir = os.path.join(project_root, "photos")
image_chop_ids = set()

for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.startswith('2006B02') and file.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename_base = Path(file).stem
            image_chop_ids.add(filename_base)

print(f"\nImages found for Study 2006: {len(image_chop_ids)}")
print(f"Sample image IDs: {sorted(list(image_chop_ids))[:5]}")

# Identify Study 2006 records to keep (those with matching images)
study_2006_mask = df['study_number'] == 2006
study_2006_with_images = df[study_2006_mask & df['standardized_chop_id'].isin(image_chop_ids)]
study_2006_without_images = df[study_2006_mask & ~df['standardized_chop_id'].isin(image_chop_ids)]

print(f"\nStudy 2006 records WITH images: {len(study_2006_with_images)}")
print(f"Study 2006 records WITHOUT images (to be removed): {len(study_2006_without_images)}")

# Remove records without images
df_cleaned = df[~(study_2006_mask & ~df['standardized_chop_id'].isin(image_chop_ids))]

final_count = len(df_cleaned)
study_2006_final = len(df_cleaned[df_cleaned['study_number'] == 2006])

print(f"\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"\nTotal records after cleaning: {final_count}")
print(f"Records removed: {initial_count - final_count}")
print(f"Study 2006 records remaining: {study_2006_final}")

# Show which chops remain
remaining_chops = df_cleaned[df_cleaned['study_number'] == 2006]['standardized_chop_id'].tolist()
print(f"\nRemaining Study 2006 chops:")
for chop_id in sorted(remaining_chops):
    print(f"  {chop_id}")

# Save cleaned data
print(f"\n" + "="*80)
print("SAVING CLEANED DATA")
print("="*80)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Backup before cleaning
backup_path = os.path.join(project_root, "database", f"consolidated_data_before_2006_cleanup_{timestamp}.csv")
df.to_csv(backup_path, index=False)
print(f"✓ Backup saved: consolidated_data_before_2006_cleanup_{timestamp}.csv")

# Save cleaned version
df_cleaned.to_csv(csv_path, index=False)
print(f"✓ Updated: consolidated_data_latest.csv")

# Update other timestamped files
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv"):
        if "latest" not in file and "backup" not in file:
            file_path = os.path.join(project_root, "database", file)
            try:
                df_cleaned.to_csv(file_path, index=False)
                print(f"✓ Updated: {file}")
            except PermissionError:
                print(f"⚠ Skipped (file open): {file}")

print(f"\n" + "="*80)
print("✓ STUDY 2006 CLEANUP COMPLETE")
print("="*80)
print(f"\nNow all Study 2006 records ({study_2006_final}) have matching images!")
