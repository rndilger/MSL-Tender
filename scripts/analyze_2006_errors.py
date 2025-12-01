"""
Identify transcription errors in Study 2006 by looking for patterns
"""
import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

# Load database
df = pd.read_csv(r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv")
study_2006 = df[df['study_number'] == 2006].copy()

# Extract chop numbers from database
db_chops = {}
for idx, row in study_2006.iterrows():
    chop_str = str(row['standardized_chop_id'])
    if 'C' in chop_str and 'D' in chop_str:
        c_pos = chop_str.index('C')
        d_pos = chop_str.index('D')
        chop_num = int(chop_str[c_pos+1:d_pos])
        db_chops[chop_num] = {
            'chop_id': chop_str,
            'original_id': row['original_chop_id'],
            'row_idx': idx
        }

# Scan images
photos_dir = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\photos"
image_chops = {}
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.startswith('2006B02') and file.lower().endswith(('.jpg', '.jpeg')):
            filename_base = Path(file).stem
            if 'C' in filename_base and 'D' in filename_base:
                c_pos = filename_base.index('C')
                d_pos = filename_base.index('D')
                chop_num = int(filename_base[c_pos+1:d_pos])
                image_chops[chop_num] = {
                    'filename': file,
                    'folder': os.path.basename(root)
                }

print("="*80)
print("STUDY 2006 TRANSCRIPTION ERROR ANALYSIS")
print("="*80)

# Check if original_chop_id matches anything
print("\n1. Checking if ORIGINAL_CHOP_ID matches image chop numbers...")
matches_via_original = []
for db_num, db_info in db_chops.items():
    orig_id = db_info['original_id']
    if pd.notna(orig_id):
        orig_num = int(orig_id)
        if orig_num in image_chops:
            matches_via_original.append({
                'db_standardized_num': db_num,
                'original_chop_id': orig_num,
                'image_num': orig_num,
                'likely_correct': orig_num
            })

print(f"   Found {len(matches_via_original)} matches using original_chop_id!")
if matches_via_original:
    print("   Sample matches:")
    for m in matches_via_original[:10]:
        print(f"      DB standardized: {m['db_standardized_num']} -> Original: {m['original_chop_id']} -> Image: {m['image_num']}")

# Check for digit transposition errors (e.g., 12 vs 21, 134 vs 143)
print("\n2. Checking for digit transposition errors...")
def get_transpositions(num):
    """Generate possible transpositions of a number"""
    s = str(num).zfill(4)
    transpositions = set()
    for i in range(len(s)-1):
        t = list(s)
        t[i], t[i+1] = t[i+1], t[i]
        transpositions.add(int(''.join(t)))
    return transpositions

transposition_matches = []
for db_num in db_chops.keys():
    for trans_num in get_transpositions(db_num):
        if trans_num in image_chops:
            transposition_matches.append({
                'db_num': db_num,
                'image_num': trans_num,
                'type': 'transposition'
            })

print(f"   Found {len(transposition_matches)} possible transposition errors")
if transposition_matches:
    print("   Sample:")
    for m in transposition_matches[:5]:
        print(f"      DB: {m['db_num']} <-> Image: {m['image_num']}")

# Check for single digit errors (off by 1-2 digits)
print("\n3. Checking for single digit misreads (e.g., 3 vs 5, 1 vs 7)...")
similar_digit_pairs = {
    '0': ['8', '6'],
    '1': ['7', '4'],
    '3': ['5', '8'],
    '5': ['3', '6'],
    '6': ['5', '8', '0'],
    '7': ['1'],
    '8': ['3', '6', '0', '9']
}

def get_similar_numbers(num):
    """Generate numbers with similar-looking digits"""
    s = str(num).zfill(4)
    similar = set()
    for i, digit in enumerate(s):
        if digit in similar_digit_pairs:
            for similar_digit in similar_digit_pairs[digit]:
                new_s = s[:i] + similar_digit + s[i+1:]
                similar.add(int(new_s))
    return similar

single_digit_matches = []
for db_num in db_chops.keys():
    for similar_num in get_similar_numbers(db_num):
        if similar_num in image_chops:
            single_digit_matches.append({
                'db_num': db_num,
                'image_num': similar_num,
                'type': 'similar_digit'
            })

print(f"   Found {len(single_digit_matches)} possible digit misread errors")
if single_digit_matches:
    print("   Sample:")
    for m in single_digit_matches[:5]:
        print(f"      DB: {m['db_num']} <-> Image: {m['image_num']}")

# Check for missing/extra leading zero (e.g., 003 vs 3, 012 vs 12)
print("\n4. Checking for leading zero issues...")
leading_zero_matches = []
for db_num in db_chops.keys():
    # Check if adding leading zero helps
    check_nums = [db_num * 10, db_num * 100]
    for check in check_nums:
        if check in image_chops:
            leading_zero_matches.append({
                'db_num': db_num,
                'image_num': check,
                'type': 'leading_zero'
            })

print(f"   Found {len(leading_zero_matches)} possible leading zero issues")

# Summary
print("\n" + "="*80)
print("SUMMARY OF POTENTIAL FIXES")
print("="*80)

total_potential_fixes = (len(matches_via_original) + len(transposition_matches) + 
                         len(single_digit_matches) + len(leading_zero_matches))

print(f"\nTotal potential matches found: {total_potential_fixes}")
print(f"  - Via original_chop_id: {len(matches_via_original)}")
print(f"  - Transposition errors: {len(transposition_matches)}")
print(f"  - Similar digit errors: {len(single_digit_matches)}")
print(f"  - Leading zero issues: {len(leading_zero_matches)}")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

if matches_via_original:
    print("\n✓ BEST APPROACH: Use original_chop_id column!")
    print(f"  The original_chop_id in the database matches {len(matches_via_original)} image filenames")
    print("  This suggests the standardized_chop_id was incorrectly created")
    print("\nAction: Fix standardized_chop_id to match original_chop_id for these records")
else:
    print("\nNeed to investigate further - checking for patterns...")

# Save detailed report
print("\n\nGenerating detailed report...")
with open(r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\scripts\2006_error_analysis.txt", 'w') as f:
    f.write("STUDY 2006 ERROR ANALYSIS\n")
    f.write("="*80 + "\n\n")
    
    if matches_via_original:
        f.write("MATCHES VIA ORIGINAL_CHOP_ID:\n")
        f.write("-"*80 + "\n")
        for m in matches_via_original:
            f.write(f"DB Standardized: {m['db_standardized_num']:04d} | ")
            f.write(f"Original ID: {m['original_chop_id']:04d} | ")
            f.write(f"Image: {m['image_num']:04d}\n")
    
    if transposition_matches:
        f.write("\n\nTRANSPOSITION ERRORS:\n")
        f.write("-"*80 + "\n")
        for m in transposition_matches:
            f.write(f"DB: {m['db_num']:04d} <-> Image: {m['image_num']:04d}\n")
    
    if single_digit_matches:
        f.write("\n\nSIMILAR DIGIT ERRORS:\n")
        f.write("-"*80 + "\n")
        for m in single_digit_matches:
            f.write(f"DB: {m['db_num']:04d} <-> Image: {m['image_num']:04d}\n")

print("✓ Report saved to scripts/2006_error_analysis.txt")
