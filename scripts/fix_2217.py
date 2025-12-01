"""
Analyze and fix Study 2217 mismatches
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")

print("="*80)
print("STUDY 2217 ANALYSIS")
print("="*80)

df = pd.read_csv(csv_path)
study_2217 = df[df['study_number'] == 2217].copy()

print(f"\nDatabase records for Study 2217: {len(study_2217)}")

# Get images
image_chop_ids = set()
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.startswith('2217') and file.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename_base = Path(file).stem
            image_chop_ids.add(filename_base)

print(f"Images found for Study 2217: {len(image_chop_ids)}")

# Compare
db_ids = set(study_2217['standardized_chop_id'].dropna())
matched = db_ids.intersection(image_chop_ids)
db_only = db_ids - image_chop_ids
images_only = image_chop_ids - db_ids

print(f"\nMatched: {len(matched)}")
print(f"DB only (no image): {len(db_only)}")
print(f"Images only (no DB): {len(images_only)}")
print(f"\nSample DB IDs: {sorted(db_only)[:10]}")
print(f"Sample image IDs: {sorted(images_only)[:10]}")

# Cleanup
print("\n" + "="*80)
print("REMOVING UNMATCHED RECORDS")
print("="*80)

initial_count = len(df)
df_cleaned = df[~((df['study_number'] == 2217) & ~df['standardized_chop_id'].isin(image_chop_ids))]
final_count = len(df_cleaned)

print(f"\nTotal records: {initial_count} → {final_count}")
print(f"Study 2217 records: {len(study_2217)} → {len(df_cleaned[df_cleaned['study_number'] == 2217])}")
print(f"Records removed: {initial_count - final_count}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(project_root, "database", f"consolidated_data_before_2217_cleanup_{timestamp}.csv")
df.to_csv(backup_path, index=False)

df_cleaned.to_csv(csv_path, index=False)
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv"):
        if "latest" not in file and "backup" not in file and "before" not in file:
            try:
                df_cleaned.to_csv(os.path.join(project_root, "database", file), index=False)
            except:
                pass

print(f"\n✓ STUDY 2217 CLEANUP COMPLETE")
