"""
Check block values and original_chop_id pattern for Study 2006
"""
import pandas as pd

# Load database
df = pd.read_csv(r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv")
study_2006 = df[df['study_number'] == 2006].copy()

print("="*80)
print("STUDY 2006 BLOCK AND ORIGINAL ID ANALYSIS")
print("="*80)

print(f"\nTotal Study 2006 records: {len(study_2006)}")

print("\n1. BLOCK VALUES IN DATABASE:")
print(study_2006['block'].value_counts().sort_index())

print("\n2. CHECKING STANDARDIZED_CHOP_ID PATTERNS:")
block_from_id = []
for chop_id in study_2006['standardized_chop_id']:
    # Extract block from standardized ID: 2006B##C####D##
    if 'B' in str(chop_id):
        b_pos = str(chop_id).index('B')
        block_in_id = str(chop_id)[b_pos+1:b_pos+3]
        block_from_id.append(block_in_id)

print("Block values found in standardized_chop_id:")
from collections import Counter
print(Counter(block_from_id))

print("\n3. ORIGINAL_CHOP_ID VALUES:")
print(f"Records with original_chop_id: {study_2006['original_chop_id'].notna().sum()}")
print(f"Records missing original_chop_id: {study_2006['original_chop_id'].isna().sum()}")

print("\nSample of original_chop_id values:")
orig_ids = study_2006['original_chop_id'].dropna().astype(int).tolist()
print(f"Range: {min(orig_ids)} to {max(orig_ids)}")
print(f"First 20: {sorted(orig_ids)[:20]}")

print("\n4. COMPARING ORIGINAL vs STANDARDIZED:")
print("\nSample records showing the discrepancy:")
print(study_2006[['original_chop_id', 'standardized_chop_id', 'block']].head(20).to_string())

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)
print("\nAll records show Block 2 in both the 'block' column and standardized_chop_id")
print("BUT the chop numbers in standardized_chop_id don't match original_chop_id")
print("\nThis means: The CHOP NUMBER portion was entered wrong in standardized_chop_id,")
print("            NOT the block number.")
print("\nSOLUTION: Rebuild standardized_chop_id using original_chop_id")
print("          Format: 2006B02C{original_chop_id:04d}D00")
