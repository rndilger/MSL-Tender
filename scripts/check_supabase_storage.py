from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
supabase = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
    os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
)

# List all storage buckets
print("Checking storage buckets...")
try:
    buckets = supabase.storage.list_buckets()
    print(f"\nTotal buckets: {len(buckets)}")
    for bucket in buckets:
        print(f"\nBucket: {bucket['name']}")
        print(f"  ID: {bucket['id']}")
        print(f"  Public: {bucket.get('public', False)}")
        print(f"  Created: {bucket.get('created_at', 'N/A')}")
        
        # Try to list files in bucket
        try:
            files = supabase.storage.from_(bucket['name']).list()
            print(f"  Files: {len(files)}")
        except Exception as e:
            print(f"  Files: Error - {e}")
except Exception as e:
    print(f"Error listing buckets: {e}")

# Check database table sizes
print("\n" + "="*60)
print("Checking database table sizes...")
print("="*60)

# Get row counts for main tables
tables = ['pork_samples', 'sample_images', 'admin_users', 'experiments']
for table in tables:
    try:
        result = supabase.table(table).select('*', count='exact', head=True).execute()
        print(f"{table}: {result.count} rows")
    except Exception as e:
        print(f"{table}: Error - {e}")
