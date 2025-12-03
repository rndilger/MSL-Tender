-- Drop all existing policies on admin_users
DROP POLICY IF EXISTS "Public read for whitelist" ON admin_users;
DROP POLICY IF EXISTS "Super admins full access" ON admin_users;
DROP POLICY IF EXISTS "Allow anonymous read for login check" ON admin_users;
DROP POLICY IF EXISTS "Users can read own record" ON admin_users;
DROP POLICY IF EXISTS "Authenticated users can read all" ON admin_users;
DROP POLICY IF EXISTS "Super admins can modify" ON admin_users;

-- Create simple, non-recursive policies

-- 1. Allow anonymous (unauthenticated) users to SELECT for login whitelist check
CREATE POLICY "anon_select"
ON admin_users
FOR SELECT
TO anon
USING (true);

-- 2. Allow authenticated users to SELECT all records
CREATE POLICY "authenticated_select"
ON admin_users
FOR SELECT
TO authenticated
USING (true);

-- 3. Allow authenticated users to INSERT/UPDATE/DELETE (we'll handle super_admin checks in application layer)
CREATE POLICY "authenticated_write"
ON admin_users
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Verify policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename = 'admin_users';
