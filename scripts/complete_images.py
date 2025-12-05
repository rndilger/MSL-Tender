"""
Add remaining sample_images (only run if images < samples)
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔗 Connecting to {NEW_URL}...")
client = create_client(NEW_URL, NEW_KEY)

# Check current counts
samples_count = client.table('pork_samples').select('*', count='exact').execute()
images_count = client.table('sample_images').select('*', count='exact').execute()

print(f"\n📊 Current state:")
print(f"   pork_samples:   {samples_count.count}")
print(f"   sample_images:  {images_count.count}")
print(f"   Missing:        {samples_count.count - images_count.count}")

if samples_count.count == images_count.count:
    print("\n✅ All samples have images! Nothing to do.")
    exit(0)

# Get samples that don't have images yet
print("\n🔍 Finding samples without images...")

# Get all sample IDs with images
existing_images = client.table('sample_images').select('sample_id').execute()
existing_sample_ids = {img['sample_id'] for img in existing_images.data}

# Get all samples, handling pagination
print("📥 Fetching all samples...")
all_samples = []
offset = 0
batch_size = 1000

while True:
    batch = client.table('pork_samples').select('id, standardized_chop_id').range(offset, offset + batch_size - 1).execute()
    all_samples.extend(batch.data)
    print(f"   Fetched {len(all_samples)} samples so far...")
    
    if len(batch.data) < batch_size:
        break
    offset += batch_size

print(f"✅ Total samples fetched: {len(all_samples)}")

# Find samples without images
samples_without_images = [s for s in all_samples if s['id'] not in existing_sample_ids]
print(f"\n📋 Found {len(samples_without_images)} samples without images")

if not samples_without_images:
    print("✅ All samples have images!")
    exit(0)

# Create image records
base_url = "https://pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev"
images = []
for sample in samples_without_images:
    images.append({
        'sample_id': sample['id'],
        'image_type': 'chop',
        'image_url': f"{base_url}/{sample['standardized_chop_id']}.jpg"
    })

# Insert in batches
print(f"\n💾 Inserting {len(images)} image records...")
batch_size = 100
for i in range(0, len(images), batch_size):
    batch = images[i:i + batch_size]
    client.table('sample_images').insert(batch).execute()
    print(f"✅ Inserted batch {i//batch_size + 1} ({i + len(batch)}/{len(images)})")

# Final verification
final_count = client.table('sample_images').select('*', count='exact').execute()
print(f"\n✅ Final image count: {final_count.count}")
