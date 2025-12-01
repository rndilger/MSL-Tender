"""
Fix remaining minor mismatches across all studies
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")

print("="*80)
print("FINAL CLEANUP - ALL REMAINING STUDIES")
print("="*80)

df = pd.read_csv(csv_path)

# Get all images
all_image_chop_ids = set()
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename_base = Path(file).stem
            all_image_chop_ids.add(filename_base)

print(f"Total images found: {len(all_image_chop_ids)}")
print(f"Total database records: {len(df)}")

# Check each study for mismatches
studies_to_check = [2003, 2004, 2014, 2108, 2110, 2116, 2307]
removal_summary = {}

for study_num in studies_to_check:
    study_df = df[df['study_number'] == study_num]
    db_ids = set(study_df['standardized_chop_id'].dropna())
    
    study_images = {img for img in all_image_chop_ids if img.startswith(str(study_num))}
    matched = db_ids.intersection(study_images)
    db_only = db_ids - study_images
    
    if len(db_only) > 0:
        removal_summary[study_num] = {
            'total_records': len(study_df),
            'db_only': len(db_only),
            'sample_missing': sorted(db_only)[:5]
        }
        print(f"\nStudy {study_num}: {len(study_df)} records, {len(db_only)} without images")
        print(f"  Missing: {sorted(db_only)[:5]}")

# Remove all DB records without images
print("\n" + "="*80)
print("REMOVING ALL UNMATCHED RECORDS")
print("="*80)

initial_count = len(df)
df_cleaned = df[df['standardized_chop_id'].isin(all_image_chop_ids)]
final_count = len(df_cleaned)

print(f"\nTotal records: {initial_count} → {final_count}")
print(f"Records removed: {initial_count - final_count}")

# Show study-by-study changes
for study_num in studies_to_check:
    before = len(df[df['study_number'] == study_num])
    after = len(df_cleaned[df_cleaned['study_number'] == study_num])
    if before != after:
        print(f"Study {study_num}: {before} → {after} (-{before-after})")

# Save backup and update
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(project_root, "database", f"consolidated_data_before_final_cleanup_{timestamp}.csv")
df.to_csv(backup_path, index=False)

df_cleaned.to_csv(csv_path, index=False)
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv"):
        if "latest" not in file and "backup" not in file and "before" not in file:
            try:
                df_cleaned.to_csv(os.path.join(project_root, "database", file), index=False)
            except:
                pass

print(f"\n✓ FINAL CLEANUP COMPLETE")
