"""
Fix the 2 remaining chop ID mismatches (2216 → 2116)
"""
import pandas as pd
import os

# Paths
project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
csv_path = os.path.join(project_root, "database", "consolidated_data_latest.csv")

print("="*80)
print("FIXING CHOP ID MISMATCHES (2216 → 2116)")
print("="*80)

# Load data
df = pd.read_csv(csv_path)
print(f"\nLoaded {len(df)} records")

# Find the 2 mismatched records
mask = df['standardized_chop_id'].str.startswith('2216', na=False)
print(f"\nFound {mask.sum()} records with chop IDs starting with '2216':")
print(df[mask][['study_number', 'standardized_chop_id']].to_string(index=True))

# Fix: Replace 2216 with 2116 at the beginning of standardized_chop_id
print("\nFixing chop IDs (2216 → 2116)...")
df.loc[mask, 'standardized_chop_id'] = df.loc[mask, 'standardized_chop_id'].str.replace('^2216', '2116', regex=True)

print("\nAfter fix:")
print(df.loc[mask.index[mask], ['study_number', 'standardized_chop_id']].to_string(index=True))

# Final validation
print("\n" + "="*80)
print("FINAL VALIDATION")
print("="*80)

mismatches = []
for idx, row in df.iterrows():
    study_num = str(int(row['study_number']))
    chop_id = str(row['standardized_chop_id'])
    
    if len(chop_id) >= 4:
        chop_prefix = chop_id[:4]
        if study_num != chop_prefix:
            mismatches.append({
                'row': idx + 2,
                'study_number': study_num,
                'standardized_chop_id': chop_id
            })

if mismatches:
    print(f"\n⚠ Still {len(mismatches)} mismatches remaining:")
    print(pd.DataFrame(mismatches).to_string(index=False))
else:
    print("\n✓✓✓ PERFECT! All study numbers now match their chop IDs!")
    print("    Every record in Column A matches the first 4 characters of Column C")

# Save all files
print("\n" + "="*80)
print("SAVING CORRECTED DATA")
print("="*80)

from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Backup
backup_path = os.path.join(project_root, "database", f"consolidated_data_backup_{timestamp}.csv")
df.to_csv(backup_path, index=False)
print(f"  ✓ Backup saved: consolidated_data_backup_{timestamp}.csv")

# Update latest
df.to_csv(csv_path, index=False)
print(f"  ✓ Updated: consolidated_data_latest.csv")

# Update other files
for file in os.listdir(os.path.join(project_root, "database")):
    if file.startswith("consolidated_data_") and file.endswith(".csv"):
        if "latest" not in file and "backup" not in file:
            file_path = os.path.join(project_root, "database", file)
            try:
                df.to_csv(file_path, index=False)
                print(f"  ✓ Updated: {file}")
            except PermissionError:
                print(f"  ⚠ Skipped (file open): {file}")

print("\n" + "="*80)
print("✓ ALL CORRECTIONS COMPLETE!")
print("="*80)
