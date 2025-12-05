"""
Export data from old Supabase as SQL INSERT statements
"""

import os
from supabase import create_client, Client

# Old Supabase project credentials
OLD_URL = "https://lqnxzgphdbowkzyphmqs.supabase.co"
OLD_KEY = input("Enter OLD Supabase Service Role Key: ").strip()

print(f"\n📤 Exporting data from {OLD_URL}...\n")

# Initialize client
old_supabase: Client = create_client(OLD_URL, OLD_KEY)

def export_admin_users():
    """Export admin_users as SQL"""
    print("Fetching admin_users...")
    result = old_supabase.table('admin_users').select('*').execute()
    
    if not result.data:
        return ""
    
    sql = "-- Admin Users\n"
    for row in result.data:
        sql += f"INSERT INTO admin_users (id, email, full_name, role, active, created_at) VALUES (\n"
        sql += f"  '9a94813b-bb64-46bf-9fde-e4605396853d',\n"  # New user ID
        sql += f"  '{row['email']}',\n"
        sql += f"  {f\"'{row['full_name']}'\" if row.get('full_name') else 'NULL'},\n"
        sql += f"  '{row['role']}',\n"
        sql += f"  {str(row['active']).lower()},\n"
        sql += f"  NOW()\n"
        sql += f");\n\n"
    
    print(f"✅ Exported {len(result.data)} admin users")
    return sql

def export_table_count(table_name):
    """Get count of rows in a table"""
    result = old_supabase.table(table_name).select('*', count='exact').execute()
    return result.count

try:
    # Get counts
    print("📊 Counting records...")
    admin_count = export_table_count('admin_users')
    samples_count = export_table_count('pork_samples')
    images_count = export_table_count('sample_images')
    
    print(f"\n📋 Records to export:")
    print(f"   admin_users:    {admin_count}")
    print(f"   pork_samples:   {samples_count}")
    print(f"   sample_images:  {images_count}")
    
    # Export admin users
    print(f"\n📤 Exporting...")
    sql_output = export_admin_users()
    
    # Save to file
    output_file = "database/migration_data.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_output)
    
    print(f"\n✅ Exported admin_users to {output_file}")
    print(f"\n⚠️  Note: For the large datasets (pork_samples and sample_images),")
    print(f"   we'll use a Python script to copy them directly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
