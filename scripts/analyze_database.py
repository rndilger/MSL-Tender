"""
Analyze what data is actually in the database
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def analyze_database():
    """Analyze database contents"""
    
    print("🔧 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all samples
    print("📊 Fetching all samples from database...")
    response = supabase.table("pork_samples").select("study_number, standardized_chop_id").execute()
    samples = response.data
    
    print(f"\n📈 Database Statistics:")
    print(f"   Total samples: {len(samples)}")
    
    # Count by study
    studies = Counter(sample['study_number'] for sample in samples)
    print(f"\n📚 Samples by Study Number:")
    for study in sorted(studies.keys()):
        print(f"   Study {study}: {studies[study]} samples")
    
    # Show first and last few IDs
    ids = sorted([s['standardized_chop_id'] for s in samples])
    print(f"\n📝 Sample ID Range:")
    print(f"   First 5: {', '.join(ids[:5])}")
    print(f"   Last 5: {', '.join(ids[-5:])}")
    
    # Check for study 2205
    study_2205 = [s for s in samples if s['study_number'] == 2205]
    print(f"\n🔍 Study 2205 specifically:")
    print(f"   Found: {len(study_2205)} samples")
    if study_2205:
        ids_2205 = sorted([s['standardized_chop_id'] for s in study_2205])
        print(f"   Sample IDs: {', '.join(ids_2205[:10])}...")

if __name__ == "__main__":
    analyze_database()
