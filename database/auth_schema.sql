-- ============================================
-- MSL-Tender Authentication Schema
-- Email Whitelist Implementation (Free Tier)
-- ============================================

-- Drop existing policies and tables if re-running
DROP POLICY IF EXISTS "Super admins can manage admin users" ON admin_users;
DROP POLICY IF EXISTS "Users can view own admin record" ON admin_users;
DROP POLICY IF EXISTS "Admins can manage experiments" ON experiments;
DROP POLICY IF EXISTS "Public can view active experiments" ON experiments;
DROP POLICY IF EXISTS "Admins can view samples" ON pork_samples;
DROP POLICY IF EXISTS "Public can view experiment samples" ON pork_samples;
DROP POLICY IF EXISTS "Anyone can submit responses" ON responses;
DROP POLICY IF EXISTS "Admins can view responses" ON responses;
DROP POLICY IF EXISTS "Users can view own responses" ON responses;
DROP POLICY IF EXISTS "Anyone can create session" ON participant_sessions;
DROP POLICY IF EXISTS "Admins can view sessions" ON participant_sessions;
DROP POLICY IF EXISTS "Users can view own sessions" ON participant_sessions;

DROP FUNCTION IF EXISTS is_admin();
DROP TABLE IF EXISTS admin_users CASCADE;

-- ============================================
-- ADMIN USERS TABLE
-- ============================================

CREATE TABLE admin_users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'super_admin')),
  is_active BOOLEAN DEFAULT true,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  added_by UUID REFERENCES auth.users(id),
  last_login TIMESTAMP WITH TIME ZONE
);

-- Add comment
COMMENT ON TABLE admin_users IS 'Whitelist of authorized admin users with @illinois.edu emails';

-- Create indexes for performance
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_active ON admin_users(is_active);
CREATE INDEX idx_admin_users_role ON admin_users(role);

-- Enable Row Level Security
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- ============================================
-- HELPER FUNCTION
-- ============================================

-- Function to check if current user is an active admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid()
    AND is_active = true
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION is_admin() IS 'Returns true if the current user is an active admin';

-- ============================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================

-- ADMIN_USERS TABLE POLICIES
-- Only super_admins can manage admin_users table
CREATE POLICY "Super admins can manage admin users"
ON admin_users FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid() 
    AND role = 'super_admin' 
    AND is_active = true
  )
);

-- All authenticated users can view their own record
CREATE POLICY "Users can view own admin record"
ON admin_users FOR SELECT
USING (id = auth.uid());

-- EXPERIMENTS TABLE POLICIES
-- Admins can manage experiments (create surveys)
CREATE POLICY "Admins can manage experiments"
ON experiments FOR ALL
USING (is_admin());

-- Public can view active experiments (for survey access)
CREATE POLICY "Public can view active experiments"
ON experiments FOR SELECT
USING (status = 'active');

-- PORK_SAMPLES TABLE POLICIES
-- Admins can view all samples (for creating experiments)
CREATE POLICY "Admins can view samples"
ON pork_samples FOR SELECT
USING (is_admin());

-- Public can view samples that are part of active experiments
CREATE POLICY "Public can view experiment samples"
ON pork_samples FOR SELECT
USING (
  id IN (
    SELECT sample_id FROM experiment_samples es
    JOIN experiments e ON es.experiment_id = e.id
    WHERE e.status = 'active'
  )
);

-- RESPONSES TABLE POLICIES
-- Anyone can insert responses (for survey submissions)
CREATE POLICY "Anyone can submit responses"
ON responses FOR INSERT
WITH CHECK (true);

-- Admins can view all responses
CREATE POLICY "Admins can view responses"
ON responses FOR SELECT
USING (is_admin());

-- Users can view their own responses (if they authenticate later)
CREATE POLICY "Users can view own responses"
ON responses FOR SELECT
USING (
  session_id IN (
    SELECT id FROM participant_sessions
    WHERE email = auth.jwt()->>'email'
  )
);

-- PARTICIPANT_SESSIONS TABLE POLICIES
-- Anyone can create a session (for survey participation)
CREATE POLICY "Anyone can create session"
ON participant_sessions FOR INSERT
WITH CHECK (true);

-- Admins can view all sessions
CREATE POLICY "Admins can view sessions"
ON participant_sessions FOR SELECT
USING (is_admin());

-- Users can view their own sessions
CREATE POLICY "Users can view own sessions"
ON participant_sessions FOR SELECT
USING (email = auth.jwt()->>'email');

-- EXPERIMENT_SAMPLES TABLE POLICIES
-- Admins can manage experiment-sample relationships
CREATE POLICY "Admins can manage experiment samples"
ON experiment_samples FOR ALL
USING (is_admin());

-- Public can view experiment samples for active experiments
CREATE POLICY "Public can view active experiment samples"
ON experiment_samples FOR SELECT
USING (
  experiment_id IN (
    SELECT id FROM experiments WHERE status = 'active'
  )
);

-- SAMPLE_IMAGES TABLE POLICIES
-- Admins can manage sample images
CREATE POLICY "Admins can manage sample images"
ON sample_images FOR ALL
USING (is_admin());

-- Public can view images for samples in active experiments
CREATE POLICY "Public can view active experiment images"
ON sample_images FOR SELECT
USING (
  sample_id IN (
    SELECT sample_id FROM experiment_samples es
    JOIN experiments e ON es.experiment_id = e.id
    WHERE e.status = 'active'
  )
);

-- ============================================
-- INITIAL DATA SETUP
-- ============================================

-- NOTE: After the first admin signs up via magic link:
-- 1. Go to Supabase Dashboard → Authentication → Users
-- 2. Copy their UUID
-- 3. Run this INSERT with their actual UUID:

-- INSERT INTO admin_users (id, email, full_name, role, is_active)
-- VALUES (
--   '00000000-0000-0000-0000-000000000000', -- Replace with actual UUID
--   'your.email@illinois.edu',
--   'Your Name',
--   'super_admin',
--   true
-- );

-- Pre-populate additional admins (they will sign up later):
-- INSERT INTO admin_users (email, full_name, role, is_active)
-- VALUES
--   ('admin1@illinois.edu', 'Admin One', 'admin', true),
--   ('admin2@illinois.edu', 'Admin Two', 'admin', true),
--   ('admin3@illinois.edu', 'Admin Three', 'admin', true)
-- ON CONFLICT (email) DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- View all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Test is_admin() function (should return false if not logged in)
-- SELECT is_admin();

-- View all admin users
-- SELECT * FROM admin_users ORDER BY added_at DESC;

-- ============================================
-- CLEANUP (Use if you need to reset)
-- ============================================

-- To completely reset authentication setup:
-- DROP POLICY IF EXISTS "Super admins can manage admin users" ON admin_users;
-- DROP POLICY IF EXISTS "Users can view own admin record" ON admin_users;
-- DROP FUNCTION IF EXISTS is_admin();
-- DROP TABLE IF EXISTS admin_users CASCADE;
