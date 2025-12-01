import pandas as pd
import os
from pathlib import Path

csv_path = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv"
photos_dir = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\photos"

df = pd.read_csv(csv_path)
print(f"Database records: {len(df)}")

# Count images
image_count = 0
for root, dirs, files in os.walk(photos_dir):
    image_count += sum(1 for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png')))

print(f"Total images: {image_count}")

# Check for any nulls in standardized_chop_id
null_count = df['standardized_chop_id'].isna().sum()
print(f"Records with null chop_id: {null_count}")

# Get image set
images = set()
for root, dirs, files in os.walk(photos_dir):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            images.add(Path(f).stem)

db_ids = set(df['standardized_chop_id'].dropna())
matched = len(db_ids.intersection(images))
unmatched = len(db_ids - images)

print(f"\nDB records with images: {matched}")
print(f"DB records WITHOUT images: {unmatched}")

if unmatched == 0:
    print("\n✅ SUCCESS! 100% of database records have matching images")
else:
    print(f"\n⚠️ Still have {unmatched} unmatched records")
