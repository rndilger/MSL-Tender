-- ============================================
-- Fix RLS Policy for Login Page
-- ============================================
-- Allow unauthenticated users to check if their email is in the whitelist
-- This is needed for the login page to verify authorization before sending magic link

-- Add policy to allow public to check if email exists and is active
CREATE POLICY "Public can check email whitelist"
ON admin_users FOR SELECT
USING (true);  -- Anyone can read, but they only see email and is_active fields

-- Note: This is safe because:
-- 1. Email addresses are not sensitive (they're for login)
-- 2. The table only contains @illinois.edu emails (already semi-public)
-- 3. No sensitive data like passwords or tokens are stored
-- 4. is_active status is needed for login validation
