-- ============================================
-- Completely reset and fix admin_users RLS policies
-- ============================================

-- First, disable RLS temporarily to check
ALTER TABLE admin_users DISABLE ROW LEVEL SECURITY;

-- Drop ALL existing policies
DROP POLICY IF EXISTS "Super admins can manage admin users" ON admin_users;
DROP POLICY IF EXISTS "Users can view own admin record" ON admin_users;
DROP POLICY IF EXISTS "Public can check email whitelist" ON admin_users;
DROP POLICY IF EXISTS "Anyone can check admin whitelist" ON admin_users;

-- Re-enable RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Create ONLY the policies we need:

-- 1. Allow anyone (including unauthenticated) to read admin_users for whitelist check
CREATE POLICY "Public read for whitelist"
ON admin_users FOR SELECT
TO anon, authenticated
USING (true);

-- 2. Allow super admins to manage all records
CREATE POLICY "Super admins full access"
ON admin_users FOR ALL
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid() 
    AND role = 'super_admin' 
    AND is_active = true
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid() 
    AND role = 'super_admin' 
    AND is_active = true
  )
);

-- Verify the new policies
SELECT 
    policyname,
    cmd,
    roles,
    permissive
FROM pg_policies 
WHERE tablename = 'admin_users'
ORDER BY policyname;
