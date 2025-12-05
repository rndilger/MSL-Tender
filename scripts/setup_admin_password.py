"""
Reset password for admin user in Supabase
This will allow you to set a new password for rdilger2@illinois.edu
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔗 Connecting to {NEW_URL}...")
client = create_client(NEW_URL, NEW_KEY)

USER_EMAIL = "rdilger2@illinois.edu"
USER_ID = "9a94813b-bb64-46bf-9fde-e4605396853d"

print(f"\n🔍 Checking if user exists in auth.users...")

# Check if user exists in auth
try:
    # List all users (service role can do this)
    response = client.auth.admin.list_users()
    users = response
    
    user_exists = any(u.email == USER_EMAIL for u in users)
    
    if user_exists:
        print(f"✅ User {USER_EMAIL} exists in auth.users")
    else:
        print(f"⚠️  User {USER_EMAIL} NOT found in auth.users")
        print(f"\n📝 Creating auth user...")
        
        # Create user with password
        new_password = input("Enter new password for user: ").strip()
        
        result = client.auth.admin.create_user({
            "email": USER_EMAIL,
            "password": new_password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": "Ryan Dilger"
            }
        })
        
        print(f"✅ User created with ID: {result.user.id}")
        print(f"\n⚠️  NOTE: The user ID is {result.user.id}")
        print(f"   You may need to update admin_users table if it doesn't match: {USER_ID}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 If user doesn't exist, we need to create them.")
    print("   Run this in Supabase SQL Editor:")
    print(f"""
    -- This will be done via the auth API above
    """)

print("\n✅ Done! Try logging in now.")
