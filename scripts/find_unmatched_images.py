"""
Find which images don't have matching database records
"""
import os
from supabase import create_client, Client
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
IMAGES_DIR = Path("photos_staged_for_upload")

def find_unmatched_images():
    """Find images without database records"""
    
    print("🔧 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all standardized_chop_ids from database
    print("📊 Fetching sample IDs from database...")
    response = supabase.table("pork_samples").select("standardized_chop_id").execute()
    db_ids = set(sample['standardized_chop_id'] for sample in response.data)
    print(f"   Database has {len(db_ids)} sample IDs")
    
    # Get all image filenames
    print("📁 Scanning images...")
    image_stems = set()
    for pattern in ['*.JPG', '*.JPEG', '*.jpg', '*.jpeg']:
        for file in IMAGES_DIR.glob(pattern):
            image_stems.add(file.stem)
    print(f"   Found {len(image_stems)} unique image files")
    
    # Find unmatched
    unmatched = image_stems - db_ids
    matched = image_stems & db_ids
    
    print()
    print("=" * 60)
    print(f"📊 Match Results:")
    print(f"   Matched: {len(matched)}")
    print(f"   Unmatched: {len(unmatched)}")
    print("=" * 60)
    
    if unmatched:
        print()
        print(f"📝 First 20 unmatched image filenames:")
        for i, filename in enumerate(sorted(unmatched)[:20], 1):
            print(f"   {i}. {filename}")
        
        if len(unmatched) > 20:
            print(f"   ... and {len(unmatched) - 20} more")
        
        # Save full list to file
        output_file = Path("unmatched_images.txt")
        with open(output_file, 'w') as f:
            for filename in sorted(unmatched):
                f.write(f"{filename}\n")
        print()
        print(f"💾 Full list saved to: {output_file}")

if __name__ == "__main__":
    find_unmatched_images()
