"""
Check what data is currently in the NEW Supabase project
"""

from supabase import create_client

NEW_URL = "https://qmecfslaeadrfdxlcekk.supabase.co"
NEW_KEY = input("Enter NEW Supabase Service Role Key: ").strip()

client = create_client(NEW_URL, NEW_KEY)

print("\n📊 Checking NEW Supabase project...\n")

# Check each table
tables = ['admin_users', 'pork_samples', 'sample_images', 'experiments', 
          'experiment_samples', 'participant_sessions', 'responses']

for table in tables:
    try:
        result = client.table(table).select('*', count='exact').execute()
        print(f"   {table:25} {result.count:>6} rows")
    except Exception as e:
        print(f"   {table:25} ERROR: {e}")

print("\n" + "="*50)

# Sample some data
print("\n📋 Sample Admin User:")
admins = client.table('admin_users').select('*').limit(1).execute()
if admins.data:
    print(f"   Email: {admins.data[0]['email']}")
    print(f"   Role: {admins.data[0]['role']}")
    print(f"   ID: {admins.data[0]['id']}")
else:
    print("   No admin users found")

print("\n🥩 Sample Pork Sample:")
samples = client.table('pork_samples').select('*').limit(1).execute()
if samples.data:
    print(f"   ID: {samples.data[0]['standardized_chop_id']}")
    print(f"   Study: {samples.data[0]['study_number']}")
else:
    print("   No pork samples found")

print("\n🖼️  Sample Image:")
images = client.table('sample_images').select('*').limit(1).execute()
if images.data:
    print(f"   Type: {images.data[0]['image_type']}")
    print(f"   URL: {images.data[0]['image_url'][:60]}...")
else:
    print("   No images found")
