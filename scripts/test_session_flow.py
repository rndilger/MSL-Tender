#!/usr/bin/env python3
"""
Test the complete session flow to debug authentication issues.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"Supabase URL: {SUPABASE_URL}")
print(f"Anon Key (first 20 chars): {SUPABASE_ANON_KEY[:20] if SUPABASE_ANON_KEY else 'NOT SET'}...")
print(f"Service Key set: {'Yes' if SUPABASE_SERVICE_KEY else 'No'}")
print()

# Test with anon key
print("=" * 50)
print("Testing with ANON key (what the browser uses):")
print("=" * 50)

try:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Try to sign in
    email = "rdilger2@illinois.edu"
    password = input("Enter password: ")
    
    result = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    
    print(f"\n✅ Sign in successful!")
    print(f"   User ID: {result.user.id}")
    print(f"   Email: {result.user.email}")
    print(f"   Session: {'Present' if result.session else 'Missing'}")
    
    if result.session:
        print(f"   Access Token (first 50): {result.session.access_token[:50]}...")
        print(f"   Refresh Token: {'Present' if result.session.refresh_token else 'Missing'}")
        print(f"   Expires At: {result.session.expires_at}")
    
    # Now test getUser with the session
    print("\n--- Testing getUser() after sign in ---")
    user_result = client.auth.get_user()
    print(f"   getUser() returned: {user_result.user.email if user_result.user else 'No user'}")
    
    # Check admin_users table access
    print("\n--- Testing admin_users table access ---")
    admin_result = client.table('admin_users').select('*').eq('id', result.user.id).single().execute()
    print(f"   Admin user found: {admin_result.data if admin_result.data else 'No'}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
