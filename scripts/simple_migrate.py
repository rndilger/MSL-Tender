"""
Simple script to copy pork_samples and sample_images between Supabase projects
Uses direct table copy approach
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Get credentials
print("🔑 Old Supabase Credentials")
OLD_URL = input("Enter OLD Supabase URL: ").strip()
OLD_KEY = input("Enter OLD Service Role Key: ").strip()

print("\n🔑 New Supabase Credentials (from .env.local)")
NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"NEW URL: {NEW_URL}")
print(f"NEW KEY: {NEW_KEY[:20]}...")

# Create clients
print("\n📡 Connecting...")
old_client = create_client(OLD_URL, OLD_KEY)
new_client = create_client(NEW_URL, NEW_KEY)

# Test connections
print("Testing old connection...")
old_test = old_client.table('pork_samples').select('count', count='exact').execute()
print(f"✅ Old project has {old_test.count} pork_samples")

print("Testing new connection...")
new_test = new_client.table('pork_samples').select('count', count='exact').execute()
print(f"✅ New project has {new_test.count} pork_samples")

# Migrate admin_users
print("\n👤 Migrating admin_users...")
old_admins = old_client.table('admin_users').select('*').execute()
print(f"Found {len(old_admins.data)} admin users in old project")

for admin in old_admins.data:
    # Update to new user ID
    new_admin = {
        'id': '9a94813b-bb64-46bf-9fde-e4605396853d',
        'email': admin['email'],
        'full_name': admin.get('full_name'),
        'role': admin['role'],
        'active': admin['active']
    }
    try:
        new_client.table('admin_users').insert(new_admin).execute()
        print(f"✅ Migrated admin: {admin['email']}")
    except Exception as e:
        print(f"⚠️  Admin already exists or error: {e}")

# Migrate pork_samples
print("\n🥩 Migrating pork_samples...")
offset = 0
batch_size = 500
total_migrated = 0

while True:
    samples = old_client.table('pork_samples').select('*').range(offset, offset + batch_size - 1).execute()
    
    if not samples.data:
        break
    
    try:
        new_client.table('pork_samples').insert(samples.data).execute()
        total_migrated += len(samples.data)
        print(f"✅ Migrated {total_migrated} samples...")
    except Exception as e:
        print(f"❌ Error: {e}")
        break
    
    if len(samples.data) < batch_size:
        break
    
    offset += batch_size

print(f"✅ Total samples migrated: {total_migrated}")

# Migrate sample_images
print("\n🖼️  Migrating sample_images...")
offset = 0
total_migrated = 0

while True:
    images = old_client.table('sample_images').select('*').range(offset, offset + batch_size - 1).execute()
    
    if not images.data:
        break
    
    try:
        new_client.table('sample_images').insert(images.data).execute()
        total_migrated += len(images.data)
        print(f"✅ Migrated {total_migrated} images...")
    except Exception as e:
        print(f"❌ Error: {e}")
        break
    
    if len(images.data) < batch_size:
        break
    
    offset += batch_size

print(f"✅ Total images migrated: {total_migrated}")

# Verify
print("\n🔍 Verifying migration...")
new_admins = new_client.table('admin_users').select('count', count='exact').execute()
new_samples = new_client.table('pork_samples').select('count', count='exact').execute()
new_images = new_client.table('sample_images').select('count', count='exact').execute()

print(f"\n📊 New Database:")
print(f"   admin_users:    {new_admins.count}")
print(f"   pork_samples:   {new_samples.count}")
print(f"   sample_images:  {new_images.count}")

print("\n✅ Migration complete!")
