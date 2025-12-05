"""
Quick check of current data in new Supabase project
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔗 Checking {NEW_URL}...\n")
client = create_client(NEW_URL, NEW_KEY)

# Check counts
tables = {
    'admin_users': '👤',
    'pork_samples': '🥩',
    'sample_images': '🖼️',
    'experiments': '🧪',
    'experiment_samples': '🔬',
    'participant_sessions': '👥',
    'responses': '📝'
}

print("📊 Current Database State:\n")
for table, emoji in tables.items():
    try:
        result = client.table(table).select('*', count='exact').execute()
        status = "✅" if result.count > 0 else "⚠️ "
        print(f"{status} {emoji} {table:25} {result.count:>6} rows")
    except Exception as e:
        print(f"❌ {emoji} {table:25} ERROR: {str(e)[:40]}")

# Sample records
print("\n" + "="*60)
print("Sample Records:")
print("="*60)

print("\n👤 Admin User:")
admins = client.table('admin_users').select('*').limit(1).execute()
if admins.data:
    print(f"   Email: {admins.data[0]['email']}")
    print(f"   Role: {admins.data[0]['role']}")
else:
    print("   ⚠️  No admin users found - need to add one!")

print("\n🥩 Pork Sample:")
samples = client.table('pork_samples').select('*').limit(1).execute()
if samples.data:
    print(f"   ID: {samples.data[0]['standardized_chop_id']}")
    print(f"   Study: {samples.data[0]['study_number']}")
else:
    print("   ⚠️  No samples found - need to import CSV!")

print("\n🖼️  Sample Image:")
images = client.table('sample_images').select('*').limit(1).execute()
if images.data:
    print(f"   Type: {images.data[0]['image_type']}")
    print(f"   URL: {images.data[0]['image_url'][:70]}...")
else:
    print("   ⚠️  No images found - need to populate!")

print("\n" + "="*60)
