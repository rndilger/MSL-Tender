"""
Direct migration - enter all credentials manually
"""

from supabase import create_client

print("=" * 60)
print(" SUPABASE DATA MIGRATION")
print("=" * 60)

# Get OLD project credentials
print("\n📋 OLD Supabase Project (GitHub @rndpig):")
print("   URL: https://lqnxzgphdbowkzyphmqs.supabase.co")
OLD_URL = "https://lqnxzgphdbowkzyphmqs.supabase.co"
OLD_KEY = input("   Service Role Key: ").strip()

# Get NEW project credentials
print("\n📋 NEW Supabase Project (GitHub @rndilger):")
print("   URL: https://qmecfslaeadrfdxlcekk.supabase.co")
NEW_URL = "https://qmecfslaeadrfdxlcekk.supabase.co"
NEW_KEY = input("   Service Role Key: ").strip()

print("\n" + "=" * 60)
print(" CONNECTING TO DATABASES")
print("=" * 60)

# Create clients
old_client = create_client(OLD_URL, OLD_KEY)
new_client = create_client(NEW_URL, NEW_KEY)

# Test connections
print("\n🔍 Testing connections...")
try:
    old_count = old_client.table('pork_samples').select('*', count='exact').execute()
    print(f"✅ OLD project: {old_count.count} pork_samples")
except Exception as e:
    print(f"❌ Failed to connect to OLD project: {e}")
    exit(1)

try:
    new_count = new_client.table('pork_samples').select('*', count='exact').execute()
    print(f"✅ NEW project: {new_count.count} pork_samples")
except Exception as e:
    print(f"❌ Failed to connect to NEW project: {e}")
    exit(1)

print("\n" + "=" * 60)
print(" STARTING MIGRATION")
print("=" * 60)

# 1. Migrate admin_users
print("\n👤 Migrating admin_users...")
try:
    old_admins = old_client.table('admin_users').select('*').execute()
    print(f"   Found {len(old_admins.data)} admin users")
    
    for admin in old_admins.data:
        new_admin = {
            'id': '9a94813b-bb64-46bf-9fde-e4605396853d',
            'email': admin['email'],
            'full_name': admin.get('full_name'),
            'role': admin['role'],
            'active': admin['active']
        }
        try:
            new_client.table('admin_users').insert(new_admin).execute()
            print(f"   ✅ {admin['email']}")
        except Exception as e:
            if 'duplicate' in str(e).lower():
                print(f"   ⚠️  {admin['email']} (already exists)")
            else:
                print(f"   ❌ {admin['email']}: {e}")
except Exception as e:
    print(f"❌ Error migrating admin_users: {e}")

# 2. Migrate pork_samples
print("\n🥩 Migrating pork_samples...")
try:
    offset = 0
    batch_size = 500
    total = 0
    
    while True:
        batch = old_client.table('pork_samples').select('*').range(offset, offset + batch_size - 1).execute()
        
        if not batch.data:
            break
        
        new_client.table('pork_samples').insert(batch.data).execute()
        total += len(batch.data)
        print(f"   ✅ {total} samples migrated...")
        
        if len(batch.data) < batch_size:
            break
        
        offset += batch_size
    
    print(f"   ✅ Total: {total} pork_samples")
except Exception as e:
    print(f"❌ Error migrating pork_samples: {e}")

# 3. Migrate sample_images
print("\n🖼️  Migrating sample_images...")
try:
    offset = 0
    batch_size = 500
    total = 0
    
    while True:
        batch = old_client.table('sample_images').select('*').range(offset, offset + batch_size - 1).execute()
        
        if not batch.data:
            break
        
        new_client.table('sample_images').insert(batch.data).execute()
        total += len(batch.data)
        print(f"   ✅ {total} images migrated...")
        
        if len(batch.data) < batch_size:
            break
        
        offset += batch_size
    
    print(f"   ✅ Total: {total} sample_images")
except Exception as e:
    print(f"❌ Error migrating sample_images: {e}")

# 4. Verify
print("\n" + "=" * 60)
print(" VERIFICATION")
print("=" * 60)

admins = new_client.table('admin_users').select('*', count='exact').execute()
samples = new_client.table('pork_samples').select('*', count='exact').execute()
images = new_client.table('sample_images').select('*', count='exact').execute()
experiments = new_client.table('experiments').select('*', count='exact').execute()

print(f"\n📊 New Database Counts:")
print(f"   admin_users:    {admins.count}")
print(f"   pork_samples:   {samples.count}")
print(f"   sample_images:  {images.count}")
print(f"   experiments:    {experiments.count}")

print("\n✅ MIGRATION COMPLETE!")
print("\n📝 Next steps:")
print("   1. Update Vercel environment variables")
print("   2. Test local authentication")
print("   3. Deploy to production")
