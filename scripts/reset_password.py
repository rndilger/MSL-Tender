"""
Set password for admin user using Supabase Admin API
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

NEW_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
NEW_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔗 Connecting to {NEW_URL}...")
client = create_client(NEW_URL, NEW_KEY)

USER_EMAIL = "rdilger2@illinois.edu"
USER_ID = "9a94813b-bb64-46bf-9fde-e4605396853d"

print(f"\n🔐 Setting password for {USER_EMAIL}...")
new_password = getpass.getpass("Enter new password: ")
confirm_password = getpass.getpass("Confirm password: ")

if new_password != confirm_password:
    print("❌ Passwords don't match!")
    exit(1)

if len(new_password) < 6:
    print("❌ Password must be at least 6 characters!")
    exit(1)

try:
    # Update user password using admin API
    response = client.auth.admin.update_user_by_id(
        USER_ID,
        {
            "password": new_password
        }
    )
    
    print(f"✅ Password updated successfully!")
    print(f"📧 Email: {response.user.email}")
    print(f"🆔 User ID: {response.user.id}")
    print(f"\n🎉 You can now log in at http://localhost:3000/admin/login")
    print(f"   Email: {USER_EMAIL}")
    print(f"   Password: (the one you just set)")
    
except Exception as e:
    print(f"❌ Error updating password: {e}")
    print("\n💡 Alternative: Use Supabase Dashboard")
    print("   1. Go to Authentication → Users")
    print("   2. Click on rdilger2@illinois.edu")
    print("   3. Look for 'Send Password Reset Email' or 'Reset Password'")
