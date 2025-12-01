"""
Compare original_chop_id with the chop number in standardized_chop_id
"""
import pandas as pd

# Load database
df = pd.read_csv(r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv")
study_2006 = df[df['study_number'] == 2006].copy()

print("="*80)
print("COMPARING ORIGINAL vs STANDARDIZED CHOP NUMBERS")
print("="*80)

mismatches = []
matches = []

for idx, row in study_2006.iterrows():
    orig_id = int(row['original_chop_id'])
    std_id = str(row['standardized_chop_id'])
    
    # Extract chop number from standardized ID
    if 'C' in std_id and 'D' in std_id:
        c_pos = std_id.index('C')
        d_pos = std_id.index('D')
        std_chop_num = int(std_id[c_pos+1:d_pos])
        
        if orig_id == std_chop_num:
            matches.append({
                'original': orig_id,
                'standardized': std_chop_num,
                'full_id': std_id
            })
        else:
            mismatches.append({
                'original': orig_id,
                'standardized': std_chop_num,
                'full_id': std_id,
                'row_idx': idx
            })

print(f"\nMatches (original == standardized): {len(matches)}")
print(f"Mismatches (original != standardized): {len(mismatches)}")

if len(mismatches) == 0:
    print("\n✓ ALL RECORDS MATCH!")
    print("The standardized_chop_id was built correctly from original_chop_id")
    print("\nThis means the issue is:")
    print("  - The IMAGE FILENAMES don't match the original_chop_id values")
    print("  - OR the images are from a different subset/batch of the same study")
    
    print("\nLet's check what image chop numbers we have...")
    import os
    from pathlib import Path
    
    photos_dir = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\photos"
    image_chops = []
    for root, dirs, files in os.walk(photos_dir):
        for file in files:
            if file.startswith('2006B02') and file.lower().endswith(('.jpg', '.jpeg')):
                filename_base = Path(file).stem
                if 'C' in filename_base and 'D' in filename_base:
                    c_pos = filename_base.index('C')
                    d_pos = filename_base.index('D')
                    chop_num = int(filename_base[c_pos+1:d_pos])
                    image_chops.append(chop_num)
    
    orig_chops = [m['original'] for m in matches]
    
    print(f"\nDatabase has chops (from original_chop_id): {sorted(orig_chops)[:10]}...")
    print(f"Images have chops: {sorted(image_chops)[:10]}...")
    
    overlap = set(orig_chops).intersection(set(image_chops))
    print(f"\nOverlap: {len(overlap)} chops")
    print(f"DB only: {len(set(orig_chops) - set(image_chops))} chops")
    print(f"Images only: {len(set(image_chops) - set(orig_chops))} chops")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print("The database records are CORRECT.")
    print("The images represent a DIFFERENT set of chops from the same study/block.")
    print("\nPOSSIBLE SCENARIOS:")
    print("1. Images were mislabeled - should have different chop numbers")
    print("2. Images and data are from different days/sessions of same study")
    print("3. Need to find the matching Excel data for these image chop numbers")
    print("4. Need to find the matching images for the database chop numbers")

else:
    print("\n⚠ FOUND MISMATCHES!")
    print("\nShowing first 10 mismatches:")
    for m in mismatches[:10]:
        print(f"  Original: {m['original']:04d} | Standardized: {m['standardized']:04d} | {m['full_id']}")
