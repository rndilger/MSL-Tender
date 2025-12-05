"""
Populate fresh data into new Supabase project
1. Add admin user
2. Import pork samples from CSV
3. Import sample images from CSV
"""

import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔗 Connecting to {NEW_URL}...")
client = create_client(NEW_URL, NEW_KEY)

# Step 1: Add admin user
print("\n👤 Adding admin user...")
try:
    admin_data = {
        'id': '9a94813b-bb64-46bf-9fde-e4605396853d',
        'email': 'rdilger2@illinois.edu',
        'full_name': 'Ryan Dilger',
        'role': 'super_admin',
        'active': True
    }
    client.table('admin_users').insert(admin_data).execute()
    print("✅ Admin user added")
except Exception as e:
    if 'duplicate' in str(e).lower():
        print("✅ Admin user already exists")
    else:
        print(f"⚠️  Error: {e}")

# Step 2: Import pork samples
print("\n🥩 Importing pork samples...")
csv_file = 'database/consolidated_data_for_supabase.csv'

if not os.path.exists(csv_file):
    print(f"❌ File not found: {csv_file}")
    print("\nAvailable CSV files:")
    for f in os.listdir('database'):
        if f.endswith('.csv'):
            print(f"   - {f}")
    exit(1)

df = pd.read_csv(csv_file)
print(f"📊 Found {len(df)} samples in CSV")

# Convert DataFrame to list of dicts with proper type handling
import json
import numpy as np

# Define integer columns that should be converted
integer_columns = ['study_number', 'original_chop_id', 'block', 'days_aging', 'days_display']

samples = []
for _, row in df.iterrows():
    sample = {}
    for key, value in row.items():
        if pd.isna(value) or value is np.nan:
            sample[key] = None
        elif key in integer_columns:
            # Convert to integer if not None
            sample[key] = int(float(value)) if not pd.isna(value) else None
        elif isinstance(value, (np.integer, np.floating)):
            # Convert numpy types to Python types
            sample[key] = float(value)
        else:
            sample[key] = value
    samples.append(sample)

# Insert in batches
batch_size = 100
for i in range(0, len(samples), batch_size):
    batch = samples[i:i + batch_size]
    try:
        client.table('pork_samples').insert(batch).execute()
        print(f"✅ Inserted batch {i//batch_size + 1} ({i + len(batch)}/{len(samples)} samples)")
    except Exception as e:
        print(f"❌ Error in batch {i//batch_size + 1}: {e}")
        break

# Step 3: Verify sample count
result = client.table('pork_samples').select('*', count='exact').execute()
print(f"\n✅ Total pork_samples in database: {result.count}")

# Step 4: Populate sample_images from pork_samples
print("\n🖼️  Populating sample_images from pork_samples...")
samples_result = client.table('pork_samples').select('id, standardized_chop_id').execute()
samples_data = samples_result.data

print(f"📊 Creating image records for {len(samples_data)} samples...")

images = []
for sample in samples_data:
    chop_id = sample['standardized_chop_id']
    base_url = "https://pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev"
    
    images.append({
        'sample_id': sample['id'],
        'image_type': 'chop',
        'image_url': f"{base_url}/{chop_id}.jpg"
    })

# Insert images in batches
for i in range(0, len(images), batch_size):
    batch = images[i:i + batch_size]
    try:
        client.table('sample_images').insert(batch).execute()
        print(f"✅ Inserted batch {i//batch_size + 1} ({i + len(batch)}/{len(images)} images)")
    except Exception as e:
        print(f"❌ Error in batch {i//batch_size + 1}: {e}")
        break

# Final verification
print("\n🔍 Final verification...")
admin_count = client.table('admin_users').select('*', count='exact').execute()
samples_count = client.table('pork_samples').select('*', count='exact').execute()
images_count = client.table('sample_images').select('*', count='exact').execute()

print(f"\n📊 Database Summary:")
print(f"   admin_users:    {admin_count.count}")
print(f"   pork_samples:   {samples_count.count}")
print(f"   sample_images:  {images_count.count}")

print("\n✅ Population complete!")
print("\n📝 Next steps:")
print("   1. Update Vercel environment variables")
print("   2. Test local authentication")
print("   3. Delete old Supabase project")
