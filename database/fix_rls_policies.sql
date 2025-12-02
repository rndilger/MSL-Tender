-- ============================================
-- Check Current RLS Policies on admin_users
-- ============================================

-- View all policies on admin_users table
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'admin_users'
ORDER BY policyname;

-- ============================================
-- Drop the restrictive policy and add public read
-- ============================================

-- Drop the policy that blocks unauthenticated reads
DROP POLICY IF EXISTS "Users can view own admin record" ON admin_users;

-- Add new policy that allows anyone to read admin_users (for whitelist check)
CREATE POLICY "Anyone can check admin whitelist"
ON admin_users FOR SELECT
TO public
USING (true);

-- Keep the super admin management policy
-- (This already exists, just here for reference)
-- CREATE POLICY "Super admins can manage admin users"
-- ON admin_users FOR ALL
-- USING (
--   EXISTS (
--     SELECT 1 FROM admin_users
--     WHERE id = auth.uid() 
--     AND role = 'super_admin' 
--     AND is_active = true
--   )
-- );

-- ============================================
-- Verify the new policy
-- ============================================

SELECT 
    policyname,
    cmd,
    roles
FROM pg_policies 
WHERE tablename = 'admin_users';
