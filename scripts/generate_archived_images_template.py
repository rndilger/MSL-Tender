"""
Generate CSV template for 312 archived images without database records.
Parse filenames using the photo naming algorithm to pre-fill metadata.

Photo naming format: YYYYBXXCXXXXDXX
  YYYY = Study number (4 digits)
  B = Block identifier
  XX = Block number (2 digits)
  C = Carcass identifier
  XXXX = Carcass number (4 digits)
  D = Display identifier
  XX = Display day (2 digits)
"""
import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime

project_root = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
archive_dir = os.path.join(project_root, "photos_archive_no_db_record")
template_csv = os.path.join(project_root, "database", "consolidated_data_latest.csv")
output_csv = os.path.join(project_root, "database", "archived_images_template_for_completion.csv")

print("="*80)
print("GENERATING TEMPLATE FOR 312 ARCHIVED IMAGES")
print("="*80)

# Load template to get column structure
template_df = pd.read_csv(template_csv)
columns = template_df.columns.tolist()
print(f"Template columns: {len(columns)} columns")

# Parse photo naming pattern
def parse_chop_filename(filename):
    """
    Parse chop ID from filename using naming convention:
    YYYYBXXCXXXXDXX where:
    - YYYY = Study number
    - BXX = Block (B + 2 digits)
    - CXXXX = Carcass (C + 4 digits)
    - DXX = Display day (D + 2 digits)
    """
    base = Path(filename).stem
    
    # Match pattern: 4 digits, B, 2 digits, C, 4 digits, D, 2 digits
    pattern = r'^(\d{4})B(\d{2})C(\d{4})D(\d{2})'
    match = re.match(pattern, base)
    
    if match:
        study = int(match.group(1))
        block = int(match.group(2))
        carcass = int(match.group(3))
        display = int(match.group(4))
        
        return {
            'study_number': study,
            'block': block,
            'carcass_number': carcass,
            'days_display': display,
            'original_chop_id': float(carcass),
            'standardized_chop_id': base
        }
    else:
        # Fallback for non-standard filenames
        return {
            'study_number': None,
            'block': None,
            'carcass_number': None,
            'days_display': None,
            'original_chop_id': None,
            'standardized_chop_id': base
        }

# Get all archived images
archived_images = []
for file in os.listdir(archive_dir):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        archived_images.append(file)

print(f"\nFound {len(archived_images)} archived images")

# Create records for each image
records = []
for filename in sorted(archived_images):
    parsed = parse_chop_filename(filename)
    
    # Create record with template structure
    record = {}
    for col in columns:
        if col == 'study_number':
            record[col] = parsed['study_number']
        elif col == 'original_chop_id':
            record[col] = parsed['original_chop_id']
        elif col == 'standardized_chop_id':
            record[col] = parsed['standardized_chop_id']
        elif col == 'block':
            record[col] = parsed['block']
        elif col == 'days_display':
            record[col] = parsed['days_display']
        elif col == 'source_file':
            record[col] = 'archived_images_no_db_record'
        elif col == 'import_date':
            record[col] = datetime.now().isoformat()
        else:
            # Leave other fields blank for undergrad to complete
            record[col] = None
    
    records.append(record)

# Create DataFrame and save
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)

print(f"\n✓ Generated template CSV: {len(records)} records")
print(f"  Output: {output_csv}")

# Show summary statistics
print(f"\n{'='*80}")
print("PARSED DATA SUMMARY")
print(f"{'='*80}")

parsed_count = df['study_number'].notna().sum()
print(f"Successfully parsed: {parsed_count}/{len(df)} images")

if parsed_count > 0:
    print(f"\nStudies represented:")
    study_counts = df['study_number'].value_counts().sort_index()
    for study, count in study_counts.items():
        if pd.notna(study):
            print(f"  Study {int(study)}: {count} images")

unparsed = df[df['study_number'].isna()]
if len(unparsed) > 0:
    print(f"\n⚠️ Could not parse {len(unparsed)} filenames (non-standard format):")
    for idx, row in unparsed.head(10).iterrows():
        print(f"  {row['standardized_chop_id']}")

print(f"\n{'='*80}")
print("FIELDS PRE-FILLED:")
print("  ✓ study_number (from filename)")
print("  ✓ original_chop_id (carcass number)")
print("  ✓ standardized_chop_id (full filename)")
print("  ✓ block (from filename)")
print("  ✓ days_display (from filename)")
print("  ✓ source_file (marked as archived)")
print("  ✓ import_date (current timestamp)")
print("\nFIELDS TO COMPLETE (by undergrad):")
print("  • setting, sex, sireline")
print("  • days_aging")
print("  • ph")
print("  • color/marbling/firmness measurements")
print("  • minolta readings")
print("  • moisture_percent, fat_percent")
print(f"\n✅ Template ready for undergrad completion!")
