"""
Prepare consolidated CSV for Supabase import
- Convert float columns to integers where appropriate
- Handle NULL values properly
- Ensure data types match schema
"""
import pandas as pd
import numpy as np

csv_path = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_latest.csv"
output_path = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\database\consolidated_data_for_supabase.csv"

print("="*80)
print("PREPARING CSV FOR SUPABASE IMPORT")
print("="*80)

# Load data
df = pd.read_csv(csv_path)
print(f"\nLoaded {len(df)} records")

# Convert float columns to int where appropriate
int_columns = ['study_number', 'block', 'original_chop_id', 'days_aging', 'days_display']

for col in int_columns:
    if col in df.columns:
        # Convert to int, handling NaN (keep as NaN, not 0)
        df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) else np.nan)
        print(f"✓ Converted {col} to integer")

# Ensure numeric columns are proper types (DECIMAL columns)
decimal_columns = [
    'ph',
    'ventral_color', 'ventral_marbling', 'ventral_firmness',
    'minolta_ventral_l', 'minolta_ventral_a', 'minolta_ventral_b',
    'chop_color', 'chop_marbling', 'chop_firmness',
    'minolta_chop_l', 'minolta_chop_a', 'minolta_chop_b',
    'moisture_percent', 'fat_percent'
]

for col in decimal_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Handle empty strings - convert to NULL
df = df.replace('', np.nan)
df = df.replace(' ', np.nan)
df = df.replace('.', np.nan)

# Convert integer columns to proper format for CSV output
# Use Int64 dtype which supports NaN and outputs integers without .0
for col in ['study_number', 'block', 'original_chop_id', 'days_aging', 'days_display']:
    if col in df.columns:
        df[col] = df[col].astype('Int64')

# Save with proper formatting
df.to_csv(output_path, index=False, na_rep='')
print(f"\n✓ Saved cleaned CSV: {output_path}")

# Show data types
print(f"\n{'='*80}")
print("DATA TYPES")
print(f"{'='*80}")
print(df.dtypes)

print(f"\n{'='*80}")
print("SAMPLE DATA (first 3 rows)")
print(f"{'='*80}")
print(df.head(3).to_string())

print(f"\n{'='*80}")
print("NULL VALUE COUNTS")
print(f"{'='*80}")
null_counts = df.isnull().sum()
for col, count in null_counts[null_counts > 0].items():
    print(f"{col}: {count} nulls")

print(f"\n✅ CSV ready for Supabase import!")
print(f"   Use file: {output_path}")
