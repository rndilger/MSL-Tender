"""
Test authentication directly with Supabase API
This will tell us if the password is correct or if there's another issue
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

print(f"🔗 Testing authentication to {NEW_URL}...")
print(f"Using ANON key: {NEW_ANON_KEY[:20]}...\n")

# Create client with ANON key (same as the app uses)
client = create_client(NEW_URL, NEW_ANON_KEY)

USER_EMAIL = "rdilger2@illinois.edu"
print(f"📧 Email: {USER_EMAIL}")
password = getpass.getpass("🔐 Password: ")

print("\n🔄 Attempting sign in...")

try:
    # Try to sign in with password (exactly like the app does)
    response = client.auth.sign_in_with_password({
        "email": USER_EMAIL,
        "password": password
    })
    
    print("\n✅ AUTHENTICATION SUCCESSFUL!")
    print(f"User ID: {response.user.id}")
    print(f"Email: {response.user.email}")
    print(f"Session exists: {response.session is not None}")
    
    # Now check admin_users table
    print("\n🔍 Checking admin_users table...")
    admin_result = client.table('admin_users').select('*').eq('id', response.user.id).execute()
    
    if admin_result.data:
        print("✅ User found in admin_users table!")
        print(f"   Role: {admin_result.data[0]['role']}")
        print(f"   Active: {admin_result.data[0]['active']}")
    else:
        print("❌ User NOT found in admin_users table!")
        print("This is why login fails in the app!")
        
except Exception as e:
    print(f"\n❌ AUTHENTICATION FAILED!")
    print(f"Error: {e}")
    print(f"\nThis means:")
    print(f"1. Password is incorrect, OR")
    print(f"2. User doesn't exist in auth.users, OR")
    print(f"3. Email is not confirmed")
    
    print(f"\n💡 Let's check the user exists...")
    # Use service role to check
    service_client = create_client(NEW_URL, os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    try:
        users = service_client.auth.admin.list_users()
        user_exists = any(u.email == USER_EMAIL for u in users)
        if user_exists:
            print(f"✅ User exists in database")
            print(f"❌ Password must be incorrect!")
        else:
            print(f"❌ User does NOT exist in auth.users!")
    except Exception as e2:
        print(f"Error checking: {e2}")
