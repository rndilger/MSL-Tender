"""
Fix study number mismatches in consolidated dataset and validate
"""
import pandas as pd
import os

# Paths
project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")

print("="*80)
print("FIXING STUDY NUMBER MISMATCHES")
print("="*80)

# Load data
df = pd.read_csv(csv_path)
print(f"\nLoaded {len(df)} records")

# Fix: Change study 2210 to 2110
print("\nFixing Study 2210 → 2110...")
mask_2210 = df['study_number'] == 2210
count_2210 = mask_2210.sum()
df.loc[mask_2210, 'study_number'] = 2110
print(f"  ✓ Updated {count_2210} records from 2210 to 2110")

# Validation: Check that Column A (study_number) matches first 4 chars of Column C (standardized_chop_id)
print("\n" + "="*80)
print("VALIDATION: Study Number vs Standardized Chop ID")
print("="*80)

mismatches = []
for idx, row in df.iterrows():
    study_num = str(int(row['study_number']))
    chop_id = str(row['standardized_chop_id'])
    
    if len(chop_id) >= 4:
        chop_study_prefix = chop_id[:4]
        if study_num != chop_study_prefix:
            mismatches.append({
                'row': idx + 2,  # +2 for Excel row (header + 0-index)
                'study_number': study_num,
                'standardized_chop_id': chop_id,
                'chop_prefix': chop_study_prefix
            })

if mismatches:
    print(f"\n⚠ Found {len(mismatches)} mismatches:\n")
    mismatch_df = pd.DataFrame(mismatches)
    print(mismatch_df.to_string(index=False))
    
    # Group by type of mismatch
    print("\n\nMismatches by study:")
    print(mismatch_df.groupby(['study_number', 'chop_prefix']).size())
else:
    print("\n✓ PERFECT! All study numbers match their standardized chop IDs")
    print("  Every record in Column A matches the first 4 characters of Column C")

# Save the corrected file
print("\n" + "="*80)
print("SAVING CORRECTED DATA")
print("="*80)

# Save with timestamp backup
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(project_root, "database", f"consolidated_data_backup_{timestamp}.csv")
df.to_csv(backup_path, index=False)
print(f"  ✓ Backup saved: consolidated_data_backup_{timestamp}.csv")

# Overwrite latest
df.to_csv(csv_path, index=False)
print(f"  ✓ Updated: consolidated_data_latest.csv")

# Also update the other timestamped versions
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv") and file != f"consolidated_data_backup_{timestamp}.csv":
        if "latest" not in file:
            file_path = os.path.join(project_root, "database", file)
            df.to_csv(file_path, index=False)
            print(f"  ✓ Updated: {file}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total records: {len(df)}")
print(f"Study 2110 records: {(df['study_number'] == 2110).sum()}")
print(f"Study 2210 records: {(df['study_number'] == 2210).sum()}")
print(f"\n✓ Data correction complete!")
print("="*80)
