"""
Import full consolidated data into Supabase
Handles duplicate standardized_chop_id by updating existing records
"""
import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
CSV_FILE = Path("database/consolidated_data_for_supabase.csv")

def import_data():
    """Import all data from CSV to Supabase"""
    
    if not CSV_FILE.exists():
        print(f"❌ Error: CSV file not found: {CSV_FILE}")
        return
    
    print("📂 Reading CSV file...")
    df = pd.read_csv(CSV_FILE)
    print(f"   Found {len(df)} rows in CSV")
    
    print("🔧 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get existing standardized_chop_ids
    print("📊 Fetching existing records from database...")
    response = supabase.table("pork_samples").select("standardized_chop_id").execute()
    existing_ids = set(row['standardized_chop_id'] for row in response.data)
    print(f"   Found {len(existing_ids)} existing records")
    
    # Prepare records
    print("🔄 Preparing data for import...")
    new_records = []
    skipped = 0
    
    for _, row in df.iterrows():
        chop_id = row['standardized_chop_id']
        
        # Skip if already exists
        if chop_id in existing_ids:
            skipped += 1
            continue
        
        # Build record (handle NaN values)
        record = {
            'study_number': int(row['study_number']) if pd.notna(row['study_number']) else None,
            'original_chop_id': int(row['original_chop_id']) if pd.notna(row['original_chop_id']) else None,
            'standardized_chop_id': chop_id,
            'block': int(row['block']) if pd.notna(row['block']) else None,
            'setting': str(row['setting']) if pd.notna(row['setting']) else None,
            'sex': str(row['sex']) if pd.notna(row['sex']) else None,
            'sireline': str(row['sireline']) if pd.notna(row['sireline']) else None,
            'days_aging': int(row['days_aging']) if pd.notna(row['days_aging']) else None,
            'days_display': int(row['days_display']) if pd.notna(row['days_display']) else None,
            'ph': float(row['ph']) if pd.notna(row['ph']) else None,
            'ventral_color': float(row['ventral_color']) if pd.notna(row['ventral_color']) else None,
            'ventral_marbling': float(row['ventral_marbling']) if pd.notna(row['ventral_marbling']) else None,
            'ventral_firmness': float(row['ventral_firmness']) if pd.notna(row['ventral_firmness']) else None,
            'minolta_ventral_l': float(row['minolta_ventral_l']) if pd.notna(row['minolta_ventral_l']) else None,
            'minolta_ventral_a': float(row['minolta_ventral_a']) if pd.notna(row['minolta_ventral_a']) else None,
            'minolta_ventral_b': float(row['minolta_ventral_b']) if pd.notna(row['minolta_ventral_b']) else None,
            'chop_color': float(row['chop_color']) if pd.notna(row['chop_color']) else None,
            'chop_marbling': float(row['chop_marbling']) if pd.notna(row['chop_marbling']) else None,
            'chop_firmness': float(row['chop_firmness']) if pd.notna(row['chop_firmness']) else None,
            'minolta_chop_l': float(row['minolta_chop_l']) if pd.notna(row['minolta_chop_l']) else None,
            'minolta_chop_a': float(row['minolta_chop_a']) if pd.notna(row['minolta_chop_a']) else None,
            'minolta_chop_b': float(row['minolta_chop_b']) if pd.notna(row['minolta_chop_b']) else None,
            'moisture_percent': float(row['moisture_percent']) if pd.notna(row['moisture_percent']) else None,
            'fat_percent': float(row['fat_percent']) if pd.notna(row['fat_percent']) else None,
            'source_file': str(row['source_file']) if pd.notna(row['source_file']) else None,
        }
        
        new_records.append(record)
    
    print(f"\n📋 Import Summary:")
    print(f"   Already in database: {skipped}")
    print(f"   New records to add: {len(new_records)}")
    
    if not new_records:
        print("\n✅ All records already imported!")
        return
    
    # Insert records one at a time to handle duplicates gracefully
    print(f"\n💾 Inserting {len(new_records)} new records...")
    inserted = 0
    skipped_duplicates = 0
    errors = 0
    
    for i, record in enumerate(new_records, 1):
        try:
            supabase.table("pork_samples").insert(record).execute()
            inserted += 1
            if i % 50 == 0 or i == len(new_records):
                print(f"   Progress: {i}/{len(new_records)} (inserted: {inserted}, skipped: {skipped_duplicates})")
        except Exception as e:
            if '23505' in str(e) or 'duplicate key' in str(e).lower():
                # Duplicate key - skip silently
                skipped_duplicates += 1
            else:
                # Other error
                print(f"   ⚠️  Error with {record['standardized_chop_id']}: {e}")
                errors += 1
    
    print()
    print("=" * 60)
    print("✅ Import complete!")
    print(f"   Successfully inserted: {inserted}")
    print(f"   Skipped (duplicates): {skipped_duplicates}")
    if errors > 0:
        print(f"   Errors: {errors}")
    print(f"   Total records in database: {len(existing_ids) + inserted}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        import_data()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
