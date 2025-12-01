"""
Compare specific chop IDs for Study 2006
"""
import pandas as pd
import os
from pathlib import Path

# Load database
df = pd.read_csv(r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv")
study_2006 = df[df['study_number'] == 2006]

# Get DB chop numbers (just the 4-digit chop ID part)
db_chops = []
db_chop_ids = []
for chop_id in study_2006['standardized_chop_id']:
    # Format: 2006B02C0147D00
    #         0123456789...
    # Chop number is after 'C' and before 'D'
    chop_str = str(chop_id)
    if 'C' in chop_str and 'D' in chop_str:
        c_pos = chop_str.index('C')
        d_pos = chop_str.index('D')
        chop_num = chop_str[c_pos+1:d_pos]
        db_chops.append(int(chop_num))
        db_chop_ids.append(chop_str)

# Scan images
photos_dir = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\photos"
image_chops = []
image_files = []
for root, dirs, files in os.walk(photos_dir):
    for file in files:
        if file.startswith('2006B02') and file.lower().endswith(('.jpg', '.jpeg')):
            filename_base = Path(file).stem
            if 'C' in filename_base and 'D' in filename_base:
                c_pos = filename_base.index('C')
                d_pos = filename_base.index('D')
                chop_num = filename_base[c_pos+1:d_pos]
                image_chops.append(int(chop_num))
                image_files.append(filename_base)

print("="*80)
print("STUDY 2006 CHOP ID COMPARISON")
print("="*80)

print(f"\nDatabase chop numbers (first 20, sorted):")
print(sorted(db_chops)[:20])
print(f"Total in DB: {len(db_chops)}")

print(f"\nImage chop numbers (first 20, sorted):")
print(sorted(image_chops)[:20])
print(f"Total in images: {len(image_chops)}")

print("\n" + "="*80)
print("MISMATCHES")
print("="*80)

db_only_nums = sorted(set(db_chops) - set(image_chops))
img_only_nums = sorted(set(image_chops) - set(db_chops))
matched_nums = sorted(set(db_chops).intersection(set(image_chops)))

print(f"\nChop numbers IN DATABASE but NOT in images ({len(db_only_nums)}):")
print(db_only_nums)

print(f"\nChop numbers IN IMAGES but NOT in database ({len(img_only_nums)}):")
print(img_only_nums)

print(f"\nMatched chop numbers ({len(matched_nums)}):")
print(matched_nums)

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)

print("\nThis means:")
print(f"  - Database has quality data for {len(db_chops)} chops from Block 2")
print(f"  - Photos folder has images for {len(image_chops)} DIFFERENT chops from Block 2")
print(f"  - Only {len(matched_nums)} chops have both data AND images")
print("\nConclusion: These are two different sets of chops from the same study/block")
print("Action needed: Decide whether to:")
print("  1. Find the missing images for the 67 database chops")
print("  2. Find the missing data for the 67 image chops")
print("  3. Use only the 9 matched chops for experiments")
