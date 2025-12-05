"""
Verify admin user setup in new Supabase project
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

print(f"\n🔍 Checking user setup...\n")

# Check auth.users
try:
    response = client.auth.admin.list_users()
    auth_users = [u for u in response if u.email == USER_EMAIL]
    
    if auth_users:
        user = auth_users[0]
        print(f"✅ Auth User Found:")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Confirmed: {user.email_confirmed_at is not None}")
        print(f"   Last Sign In: {user.last_sign_in_at}")
        
        # Check admin_users table
        admin_result = client.table('admin_users').select('*').eq('email', USER_EMAIL).execute()
        
        if admin_result.data:
            admin = admin_result.data[0]
            print(f"\n✅ Admin User Found:")
            print(f"   Email: {admin['email']}")
            print(f"   ID: {admin['id']}")
            print(f"   Role: {admin['role']}")
            print(f"   Active: {admin['active']}")
            
            if admin['id'] == user.id:
                print(f"\n✅ IDs MATCH - Setup is correct!")
            else:
                print(f"\n❌ ID MISMATCH!")
                print(f"   Auth ID:  {user.id}")
                print(f"   Admin ID: {admin['id']}")
                print(f"\n💡 Run this SQL to fix:")
                print(f"   UPDATE admin_users SET id = '{user.id}' WHERE email = '{USER_EMAIL}';")
        else:
            print(f"\n❌ User NOT in admin_users table!")
            print(f"\n💡 Run this SQL to add:")
            print(f"   INSERT INTO admin_users (id, email, role, active)")
            print(f"   VALUES ('{user.id}', '{USER_EMAIL}', 'super_admin', true);")
    else:
        print(f"❌ User {USER_EMAIL} NOT found in auth.users!")
        print(f"\n💡 Create user in Supabase Dashboard:")
        print(f"   Authentication → Users → Add User")
        print(f"   - Email: {USER_EMAIL}")
        print(f"   - Password: (set a password)")
        print(f"   - Auto Confirm: Yes")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
