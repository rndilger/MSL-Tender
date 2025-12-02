-- ============================================
-- Create First Admin User
-- ============================================
-- This creates both the auth.users record and admin_users record
-- Replace 'your-email@illinois.edu' with your actual @illinois.edu email

-- Step 1: First, go to Supabase Dashboard → Authentication → Users
--         Click "Invite user" or "Add user"
--         Enter your @illinois.edu email address
--         Supabase will create the auth.users record and send a verification email
--         COPY THE USER ID (UUID) - you'll need it for Step 2

-- Step 2: After creating the auth user, insert into admin_users table
-- Replace 'YOUR-USER-ID-HERE' with the UUID from Step 1
-- Replace the email and name with your actual information

INSERT INTO admin_users (
    id,
    email,
    full_name,
    role,
    is_active
)
VALUES (
    'YOUR-USER-ID-HERE'::uuid,  -- Replace with UUID from Supabase Auth dashboard
    'rdilger2@illinois.edu',     -- Replace with your @illinois.edu email
    'Ryan Dilger',               -- Replace with your name
    'super_admin',               -- 'admin' or 'super_admin'
    true
);

-- Step 3: Verify the admin user was created
SELECT 
    au.id,
    au.email,
    au.full_name,
    au.role,
    au.is_active,
    u.email as auth_email,
    u.created_at
FROM admin_users au
JOIN auth.users u ON u.id = au.id
WHERE au.email = 'rdilger2@illinois.edu';  -- Replace with your email

-- ============================================
-- Alternative: If you already have an auth.users account
-- ============================================
-- If you already created an account via magic link, find your user ID:

SELECT id, email, created_at
FROM auth.users
WHERE email = 'rdilger2@illinois.edu';  -- Replace with your email

-- Then use that ID in the INSERT statement above
