"""
Test Supabase connection and verify setup
"""
from supabase import create_client, Client

# Your Supabase credentials
SUPABASE_URL = "https://vxqpbohiradglqfxwjco.supabase.co"
SUPABASE_KEY = "sb_secret_oV2hgnzK17dh6br6dZbRZw_aOKfr1DR"

print("="*80)
print("SUPABASE CONNECTION TEST")
print("="*80)

try:
    # Initialize client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✓ Connected to: {SUPABASE_URL}\n")
    
    # Test 1: Query pork_samples table
    print("Test 1: Querying pork_samples table...")
    response = supabase.table('pork_samples').select('id, study_number, standardized_chop_id').limit(5).execute()
    print(f"✓ Found {len(response.data)} sample records")
    print(f"  Sample IDs: {[s['standardized_chop_id'] for s in response.data[:3]]}")
    
    # Test 2: Count total records
    print("\nTest 2: Counting total records...")
    response = supabase.table('pork_samples').select('id', count='exact').execute()
    print(f"✓ Total pork_samples: {response.count}")
    
    # Test 3: Check experiments table
    print("\nTest 3: Checking experiments table...")
    response = supabase.table('experiments').select('*').execute()
    print(f"✓ Experiments table accessible ({len(response.data)} records)")
    
    # Test 4: Check sample_images table
    print("\nTest 4: Checking sample_images table...")
    response = supabase.table('sample_images').select('*').execute()
    print(f"✓ Sample_images table accessible ({len(response.data)} records)")
    
    # Test 5: Verify storage bucket and access image
    print("\nTest 5: Testing storage bucket...")
    files = supabase.storage.from_('pork-images').list('original')
    print(f"✓ Storage bucket accessible")
    print(f"  Files in original/ folder: {len(files)}")
    
    # Test 6: Get public URL for first image
    if files:
        test_file = files[0]['name']
        public_url = supabase.storage.from_('pork-images').get_public_url(f'original/{test_file}')
        print(f"  Sample image URL: {public_url}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
    print("Supabase is fully configured and working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nConnection test failed. Please check:")
    print("  1. Supabase URL is correct")
    print("  2. Service role key is correct")
    print("  3. Tables exist in database")
    print("  4. Storage bucket 'pork-images' exists")
