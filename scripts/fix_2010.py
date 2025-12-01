"""
Analyze and fix Study 2010 mismatches
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# Paths
project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")
photos_dir = os.path.join(project_root, "photos")

print("="*80)
print("STUDY 2010 ANALYSIS")
print("="*80)

# Load database
df = pd.read_csv(csv_path)
study_2010 = df[df['study_number'] == 2010].copy()

print(f"\nDatabase records for Study 2010: {len(study_2010)}")

# Get image chop IDs
image_chop_ids = set()
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.startswith('2010') and file.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename_base = Path(file).stem
            image_chop_ids.add(filename_base)

print(f"Images found for Study 2010: {len(image_chop_ids)}")

# Compare
db_ids = set(study_2010['standardized_chop_id'].dropna())
matched = db_ids.intersection(image_chop_ids)
db_only = db_ids - image_chop_ids
images_only = image_chop_ids - db_ids

print(f"\nMatched: {len(matched)}")
print(f"DB only (no image): {len(db_only)}")
print(f"Images only (no DB): {len(images_only)}")

# Check if original_chop_id helps
print("\n" + "="*80)
print("CHECKING ORIGINAL_CHOP_ID PATTERNS")
print("="*80)

# Extract chop numbers
db_chop_nums = []
for chop_id in study_2010['standardized_chop_id']:
    if pd.notna(chop_id) and 'C' in str(chop_id) and 'D' in str(chop_id):
        c_pos = str(chop_id).index('C')
        d_pos = str(chop_id).index('D')
        chop_num = int(str(chop_id)[c_pos+1:d_pos])
        db_chop_nums.append(chop_num)

image_chop_nums = []
for chop_id in image_chop_ids:
    if 'C' in chop_id and 'D' in chop_id:
        c_pos = chop_id.index('C')
        d_pos = chop_id.index('D')
        chop_num = int(chop_id[c_pos+1:d_pos])
        image_chop_nums.append(chop_num)

orig_ids = study_2010['original_chop_id'].dropna().astype(int).tolist()

print(f"\nDB standardized chop numbers (sample): {sorted(db_chop_nums)[:10]}")
print(f"DB original_chop_id (sample): {sorted(orig_ids)[:10]}")
print(f"Image chop numbers (sample): {sorted(image_chop_nums)[:10]}")

# Check if standardized matches original
mismatch_count = 0
for _, row in study_2010.iterrows():
    if pd.notna(row['original_chop_id']):
        orig = int(row['original_chop_id'])
        std_id = str(row['standardized_chop_id'])
        if 'C' in std_id and 'D' in std_id:
            c_pos = std_id.index('C')
            d_pos = std_id.index('D')
            std_num = int(std_id[c_pos+1:d_pos])
            if orig != std_num:
                mismatch_count += 1

if mismatch_count == 0:
    print("\n✓ Standardized IDs match original_chop_id")
else:
    print(f"\n⚠ {mismatch_count} standardized IDs don't match original_chop_id")

# Check which are missing
print("\n" + "="*80)
print("MISSING RECORDS ANALYSIS")
print("="*80)

db_without_images = study_2010[study_2010['standardized_chop_id'].isin(db_only)]
print(f"\nDB records without images: {len(db_without_images)}")
print(f"Sample missing chop IDs:")
print(sorted(db_only)[:10])

print(f"\nImages without DB records: {len(images_only)}")
print(f"Sample orphaned image IDs:")
print(sorted(images_only)[:10])

# Decision
print("\n" + "="*80)
print("CLEANUP ACTION")
print("="*80)
print(f"\nWill REMOVE {len(db_only)} database records without images")
print(f"Will KEEP {len(matched)} records with matching images")

# Perform cleanup
print("\n" + "="*80)
print("REMOVING UNMATCHED RECORDS")
print("="*80)

initial_count = len(df)
study_2010_initial = len(study_2010)

# Remove Study 2010 records without images
df_cleaned = df[~((df['study_number'] == 2010) & ~df['standardized_chop_id'].isin(image_chop_ids))]

final_count = len(df_cleaned)
study_2010_final = len(df_cleaned[df_cleaned['study_number'] == 2010])

print(f"\nTotal records: {initial_count} → {final_count}")
print(f"Study 2010 records: {study_2010_initial} → {study_2010_final}")
print(f"Records removed: {initial_count - final_count}")

# Save
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(project_root, "database", f"consolidated_data_before_2010_cleanup_{timestamp}.csv")
df.to_csv(backup_path, index=False)
print(f"\n✓ Backup saved: consolidated_data_before_2010_cleanup_{timestamp}.csv")

df_cleaned.to_csv(csv_path, index=False)
print(f"✓ Updated: consolidated_data_latest.csv")

# Update other files
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv"):
        if "latest" not in file and "backup" not in file and "before" not in file:
            file_path = os.path.join(project_root, "database", file)
            try:
                df_cleaned.to_csv(file_path, index=False)
                print(f"✓ Updated: {file}")
            except:
                pass

print(f"\n" + "="*80)
print("✓ STUDY 2010 CLEANUP COMPLETE")
print("="*80)
