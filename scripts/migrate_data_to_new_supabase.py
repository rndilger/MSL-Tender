"""
Migrate data from old Supabase project to new project
Run this script to copy pork_samples, sample_images, and admin_users data
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Old Supabase project credentials (GitHub @rndpig)
OLD_URL = "https://lqnxzgphdbowkzyphmqs.supabase.co"
OLD_KEY = input("Enter OLD Supabase Service Role Key: ").strip()

# New Supabase project credentials (GitHub @rndilger)
NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"\n🔄 Starting migration...")
print(f"FROM: {OLD_URL}")
print(f"TO:   {NEW_URL}\n")

# Initialize clients
old_supabase: Client = create_client(OLD_URL, OLD_KEY)
new_supabase: Client = create_client(NEW_URL, NEW_KEY)

def migrate_admin_users():
    """Migrate admin_users table"""
    print("📋 Migrating admin_users...")
    
    # Fetch from old
    result = old_supabase.table('admin_users').select('*').execute()
    admin_users = result.data
    
    print(f"   Found {len(admin_users)} admin users")
    
    if not admin_users:
        print("   ⚠️  No admin users to migrate")
        return
    
    # Update ID to new user ID
    for admin in admin_users:
        admin['id'] = '9a94813b-bb64-46bf-9fde-e4605396853d'
    
    # Insert into new
    result = new_supabase.table('admin_users').insert(admin_users).execute()
    print(f"   ✅ Migrated {len(admin_users)} admin users")

def migrate_pork_samples():
    """Migrate pork_samples table"""
    print("\n🥩 Migrating pork_samples...")
    
    # Fetch from old (in batches if needed)
    result = old_supabase.table('pork_samples').select('*').execute()
    samples = result.data
    
    print(f"   Found {len(samples)} pork samples")
    
    if not samples:
        print("   ⚠️  No samples to migrate")
        return
    
    # Insert in batches of 100
    batch_size = 100
    for i in range(0, len(samples), batch_size):
        batch = samples[i:i + batch_size]
        result = new_supabase.table('pork_samples').insert(batch).execute()
        print(f"   ✅ Migrated batch {i//batch_size + 1} ({len(batch)} samples)")
    
    print(f"   ✅ Total: {len(samples)} samples migrated")

def migrate_sample_images():
    """Migrate sample_images table"""
    print("\n🖼️  Migrating sample_images...")
    
    # Fetch from old
    result = old_supabase.table('sample_images').select('*').execute()
    images = result.data
    
    print(f"   Found {len(images)} sample images")
    
    if not images:
        print("   ⚠️  No images to migrate")
        return
    
    # Insert in batches of 100
    batch_size = 100
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        result = new_supabase.table('sample_images').insert(batch).execute()
        print(f"   ✅ Migrated batch {i//batch_size + 1} ({len(batch)} images)")
    
    print(f"   ✅ Total: {len(images)} images migrated")

def verify_migration():
    """Verify data was migrated successfully"""
    print("\n🔍 Verifying migration...")
    
    # Check counts
    admin_count = new_supabase.table('admin_users').select('*', count='exact').execute()
    samples_count = new_supabase.table('pork_samples').select('*', count='exact').execute()
    images_count = new_supabase.table('sample_images').select('*', count='exact').execute()
    experiments_count = new_supabase.table('experiments').select('*', count='exact').execute()
    
    print(f"\n📊 New Database Summary:")
    print(f"   admin_users:    {admin_count.count}")
    print(f"   pork_samples:   {samples_count.count}")
    print(f"   sample_images:  {images_count.count}")
    print(f"   experiments:    {experiments_count.count}")
    
    # Sample a few records
    print(f"\n👤 Sample admin user:")
    admin = new_supabase.table('admin_users').select('*').limit(1).execute()
    if admin.data:
        print(f"   Email: {admin.data[0]['email']}")
        print(f"   Role: {admin.data[0]['role']}")
        print(f"   Active: {admin.data[0]['active']}")
    
    print(f"\n🥩 Sample pork sample:")
    sample = new_supabase.table('pork_samples').select('*').limit(1).execute()
    if sample.data:
        print(f"   ID: {sample.data[0]['standardized_chop_id']}")
        print(f"   Study: {sample.data[0]['study_number']}")
    
    print(f"\n🖼️  Sample image:")
    image = new_supabase.table('sample_images').select('*').limit(1).execute()
    if image.data:
        print(f"   Type: {image.data[0]['image_type']}")
        print(f"   URL: {image.data[0]['image_url'][:60]}...")

if __name__ == "__main__":
    try:
        # Run migrations
        migrate_admin_users()
        migrate_pork_samples()
        migrate_sample_images()
        
        # Verify
        verify_migration()
        
        print("\n✅ Migration complete!")
        print("\n📝 Next steps:")
        print("1. Test login at: http://localhost:3000/admin/login")
        print("2. Update Vercel environment variables")
        print("3. Deploy to production")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\nPlease check your credentials and try again.")
