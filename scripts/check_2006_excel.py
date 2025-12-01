"""
Check original Study 2006 Excel file for additional data
"""
import pandas as pd

excel_path = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\study files\UI 20-06 Standardized Master File.xlsx"

print("="*80)
print("CHECKING ORIGINAL STUDY 2006 EXCEL FILE")
print("="*80)

try:
    df = pd.read_excel(excel_path)
    
    print(f"\nTotal rows in Excel: {len(df)}")
    print(f"\nColumns: {df.columns.tolist()}")
    
    # Check original chop IDs
    if 'Original Chop ID' in df.columns:
        orig_ids = df['Original Chop ID'].dropna().astype(int).tolist()
        print(f"\nOriginal Chop ID range: {min(orig_ids)} to {max(orig_ids)}")
        print(f"Total unique chops: {len(set(orig_ids))}")
        print(f"\nFirst 20 chop IDs: {sorted(orig_ids)[:20]}")
        print(f"Last 20 chop IDs: {sorted(orig_ids)[-20:]}")
        
        # Check if high-numbered chops exist
        high_chops = [x for x in orig_ids if x >= 100]
        low_chops = [x for x in orig_ids if x < 100]
        
        print(f"\nChops under 100: {len(low_chops)}")
        print(f"Chops 100+: {len(high_chops)}")
        
        if high_chops:
            print(f"Highest numbered chops in file: {sorted(high_chops)[-10:]}")
    
    # Check standardized chop IDs
    if 'Standardized Chop ID' in df.columns:
        print("\n" + "-"*80)
        print("Standardized Chop IDs in Excel:")
        print(df['Standardized Chop ID'].head(20).tolist())
        
except FileNotFoundError:
    print("\n⚠ Excel file not found")
    print("This is expected since study files are excluded from Git")
except Exception as e:
    print(f"\n⚠ Error reading file: {e}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("\nSince study files are local only, the consolidated CSV is our source.")
print("We'll proceed by REMOVING database records that don't have matching images.")
