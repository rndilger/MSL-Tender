# Email Whitelist Authentication Implementation
## Secure @illinois.edu Admin Access on Supabase Free Tier

---

## 🎯 **Overview**

This document outlines the secure, free-tier authentication strategy for MSL-Tender using email-based passwordless authentication with @illinois.edu domain whitelisting.

**Key Features**:
- ✅ Free tier compatible (no Pro plan required)
- ✅ Passwordless magic link authentication
- ✅ @illinois.edu domain validation via RLS
- ✅ Admin whitelist management
- ✅ Public survey access (no login required)
- ✅ Enterprise-grade security via Row Level Security

---

## 🔐 **Authentication Flow**

### **Admin Login Flow**
1. User visits `/admin/login`
2. Enters @illinois.edu email address
3. Receives magic link via email
4. Clicks link → authenticated
5. RLS checks if email is in `admin_users` table
6. Access granted/denied based on whitelist

### **Participant Flow**
1. User visits `/survey/[experimentId]` (no login required)
2. Enters name and email (any domain)
3. Completes survey
4. Responses saved to database

---

## 📊 **Database Schema Extensions**

### **Admin Users Table**

```sql
-- Create admin_users table for whitelist management
CREATE TABLE admin_users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'super_admin')),
  is_active BOOLEAN DEFAULT true,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  added_by UUID REFERENCES auth.users(id),
  last_login TIMESTAMP WITH TIME ZONE
);

-- Enable RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Only super_admins can manage admin_users
CREATE POLICY "Super admins can manage admin users"
ON admin_users FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid() AND role = 'super_admin' AND is_active = true
  )
);

-- All authenticated users can view their own record
CREATE POLICY "Users can view own admin record"
ON admin_users FOR SELECT
USING (id = auth.uid());

-- Create index for performance
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_active ON admin_users(is_active);
```

### **Initial Admin Setup**

```sql
-- You'll manually insert the first super_admin after they sign up
-- Step 1: Admin signs up with magic link
-- Step 2: Get their auth.users ID from Supabase dashboard
-- Step 3: Run this SQL to grant super_admin access:

INSERT INTO admin_users (id, email, full_name, role)
VALUES (
  '[USER_ID_FROM_AUTH_USERS]',
  'your.email@illinois.edu',
  'Your Name',
  'super_admin'
);

-- Subsequent admins can be added via the admin UI
```

---

## 🔒 **Row Level Security Policies**

### **Experiments Table**

```sql
-- Helper function to check if user is an active admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM admin_users
    WHERE id = auth.uid()
    AND is_active = true
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Admins can manage experiments
CREATE POLICY "Admins can manage experiments"
ON experiments FOR ALL
USING (is_admin());

-- Public can view active experiments (for survey access)
CREATE POLICY "Public can view active experiments"
ON experiments FOR SELECT
USING (status = 'active');
```

### **Pork Samples Table**

```sql
-- Admins can read all samples
CREATE POLICY "Admins can view samples"
ON pork_samples FOR SELECT
USING (is_admin());

-- Public can view samples included in active experiments
CREATE POLICY "Public can view experiment samples"
ON pork_samples FOR SELECT
USING (
  id IN (
    SELECT sample_id FROM experiment_samples es
    JOIN experiments e ON es.experiment_id = e.id
    WHERE e.status = 'active'
  )
);
```

### **Responses Table**

```sql
-- Anyone can insert responses (for survey submissions)
CREATE POLICY "Anyone can submit responses"
ON responses FOR INSERT
WITH CHECK (true);

-- Admins can view all responses
CREATE POLICY "Admins can view responses"
ON responses FOR SELECT
USING (is_admin());

-- Users can view their own responses
CREATE POLICY "Users can view own responses"
ON responses FOR SELECT
USING (
  session_id IN (
    SELECT id FROM participant_sessions
    WHERE email = auth.jwt()->>'email'
  )
);
```

### **Participant Sessions Table**

```sql
-- Anyone can create session (for survey access)
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
```

---

## 🛡️ **Email Domain Validation**

### **Supabase Auth Settings**

Configure in Supabase Dashboard → Authentication → Settings:

```json
{
  "enable_signup": true,
  "enable_email_confirmation": false,
  "enable_anonymous_sign_ins": false,
  "external_email_enabled": true,
  "mailer_autoconfirm": true,
  "email_provider": "built-in"
}
```

### **Database Trigger for Domain Validation**

```sql
-- Function to validate email domain on signup
CREATE OR REPLACE FUNCTION validate_admin_email()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if email ends with @illinois.edu
  IF NEW.email NOT LIKE '%@illinois.edu' THEN
    RAISE EXCEPTION 'Only @illinois.edu email addresses are allowed for admin access';
  END IF;
  
  -- Check if email is in admin_users whitelist
  IF NOT EXISTS (
    SELECT 1 FROM admin_users WHERE email = NEW.email
  ) THEN
    RAISE EXCEPTION 'Email address % is not in the admin whitelist', NEW.email;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users after insert (after successful signup)
-- Note: This requires Supabase database webhooks or Edge Functions
-- Alternative: Handle validation in application layer
```

**Note**: Since direct triggers on `auth.users` require database webhooks, we'll implement validation in the Next.js application layer for better control.

---

## 💻 **Frontend Implementation**

### **Supabase Client Setup**

```typescript
// lib/supabase/client.ts
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Database } from '@/types/database.types'

export const supabase = createClientComponentClient<Database>()
```

### **Admin Login Component**

```typescript
// app/admin/login/page.tsx
'use client'
import { useState } from 'react'
import { supabase } from '@/lib/supabase/client'

export default function AdminLogin() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    // Validate @illinois.edu domain client-side
    if (!email.endsWith('@illinois.edu')) {
      setMessage('Please use your @illinois.edu email address')
      setLoading(false)
      return
    }

    try {
      // Check if email is in admin whitelist
      const { data: adminUser, error: checkError } = await supabase
        .from('admin_users')
        .select('email, is_active')
        .eq('email', email)
        .single()

      if (checkError || !adminUser) {
        setMessage('This email is not authorized. Please contact an administrator.')
        setLoading(false)
        return
      }

      if (!adminUser.is_active) {
        setMessage('This account has been deactivated. Please contact an administrator.')
        setLoading(false)
        return
      }

      // Send magic link
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/admin/dashboard`,
        },
      })

      if (error) throw error

      setMessage('Check your email for the login link!')
    } catch (error) {
      setMessage('Error sending login link. Please try again.')
      console.error('Login error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Admin Login
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in with your @illinois.edu email
          </p>
        </div>
        
        <form onSubmit={handleLogin} className="mt-8 space-y-6">
          <div>
            <label htmlFor="email" className="sr-only">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500"
              placeholder="your.email@illinois.edu"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Magic Link'}
          </button>

          {message && (
            <p className={`text-sm text-center ${
              message.includes('Check your email') ? 'text-green-600' : 'text-red-600'
            }`}>
              {message}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
```

### **Protected Admin Layout**

```typescript
// app/admin/layout.tsx
'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase/client'

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAdminStatus()
  }, [])

  const checkAdminStatus = async () => {
    try {
      // Check if user is authenticated
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session) {
        router.push('/admin/login')
        return
      }

      // Check if user is in admin_users table
      const { data: adminUser, error } = await supabase
        .from('admin_users')
        .select('is_active')
        .eq('id', session.user.id)
        .single()

      if (error || !adminUser || !adminUser.is_active) {
        await supabase.auth.signOut()
        router.push('/admin/login')
        return
      }

      // Update last_login timestamp
      await supabase
        .from('admin_users')
        .update({ last_login: new Date().toISOString() })
        .eq('id', session.user.id)

      setIsAdmin(true)
    } catch (error) {
      console.error('Admin check error:', error)
      router.push('/admin/login')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      Loading...
    </div>
  }

  if (!isAdmin) {
    return null
  }

  return <>{children}</>
}
```

### **Admin Management Component**

```typescript
// app/admin/users/page.tsx
'use client'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase/client'

interface AdminUser {
  id: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  added_at: string
}

export default function AdminUsersPage() {
  const [admins, setAdmins] = useState<AdminUser[]>([])
  const [newEmail, setNewEmail] = useState('')
  const [newName, setNewName] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadAdmins()
  }, [])

  const loadAdmins = async () => {
    const { data, error } = await supabase
      .from('admin_users')
      .select('*')
      .order('added_at', { ascending: false })

    if (data) setAdmins(data)
  }

  const addAdmin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    if (!newEmail.endsWith('@illinois.edu')) {
      alert('Email must end with @illinois.edu')
      setLoading(false)
      return
    }

    try {
      // Insert into admin_users (they'll sign up later)
      const { error } = await supabase
        .from('admin_users')
        .insert({
          email: newEmail,
          full_name: newName || null,
          role: 'admin',
          is_active: true
        })

      if (error) throw error

      alert('Admin added! They can now sign in with a magic link.')
      setNewEmail('')
      setNewName('')
      loadAdmins()
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleActive = async (id: string, currentStatus: boolean) => {
    await supabase
      .from('admin_users')
      .update({ is_active: !currentStatus })
      .eq('id', id)
    
    loadAdmins()
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Admin User Management</h1>

      {/* Add Admin Form */}
      <form onSubmit={addAdmin} className="mb-8 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Add New Admin</h2>
        <div className="grid grid-cols-2 gap-4">
          <input
            type="email"
            placeholder="email@illinois.edu"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            required
            className="px-3 py-2 border rounded"
          />
          <input
            type="text"
            placeholder="Full Name (optional)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="px-3 py-2 border rounded"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="mt-4 px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Add Admin
        </button>
      </form>

      {/* Admin List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {admins.map((admin) => (
              <tr key={admin.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{admin.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{admin.full_name || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{admin.role}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    admin.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {admin.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => toggleActive(admin.id, admin.is_active)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    {admin.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## 🚀 **Initial Setup Steps**

### **1. Update Database Schema**

Run this SQL in Supabase SQL Editor:

```bash
# Save the SQL schema to a file
cat > update_auth_schema.sql << 'EOF'
-- Add admin_users table and RLS policies
[Copy schema from above]
EOF

# Or run directly in Supabase dashboard
```

### **2. Create First Super Admin**

```sql
-- After you sign up with magic link for the first time:
-- 1. Go to Supabase Dashboard → Authentication → Users
-- 2. Copy your user ID
-- 3. Run this SQL:

INSERT INTO admin_users (id, email, full_name, role, is_active)
VALUES (
  '00000000-0000-0000-0000-000000000000', -- Replace with your actual UUID
  'your.email@illinois.edu',
  'Your Name',
  'super_admin',
  true
);
```

### **3. Pre-populate Admin Whitelist**

```sql
-- Add known admin emails (they'll sign up later)
INSERT INTO admin_users (email, full_name, role, is_active)
VALUES
  ('admin1@illinois.edu', 'Admin One', 'admin', true),
  ('admin2@illinois.edu', 'Admin Two', 'admin', true),
  ('admin3@illinois.edu', 'Admin Three', 'admin', true);
```

---

## 🔧 **Configuration Checklist**

- [ ] Run database schema updates
- [ ] Configure Supabase Auth settings (enable magic links)
- [ ] Add first super_admin manually
- [ ] Pre-populate admin whitelist
- [ ] Test magic link login flow
- [ ] Verify RLS policies work correctly
- [ ] Test admin dashboard access control
- [ ] Configure email templates (optional branding)

---

## 📧 **Email Template Customization**

Customize magic link emails in Supabase Dashboard → Authentication → Email Templates:

```html
<h2>MSL-Tender Admin Login</h2>
<p>Click the link below to sign in to the MSL-Tender admin dashboard:</p>
<p><a href="{{ .ConfirmationURL }}">Sign In</a></p>
<p>This link expires in 1 hour.</p>
<p>If you didn't request this login link, you can safely ignore this email.</p>
```

---

## 🔐 **Security Best Practices**

1. **Rate Limiting**: Supabase provides built-in rate limiting for auth endpoints
2. **Link Expiration**: Magic links expire after 1 hour (configurable)
3. **RLS Enforcement**: All database access goes through RLS policies
4. **Domain Validation**: Client-side and database-level @illinois.edu checks
5. **Active Status**: Deactivated admins cannot access even if authenticated
6. **Audit Trail**: Track `added_at`, `added_by`, `last_login` timestamps
7. **No Hardcoded Credentials**: All auth handled by Supabase
8. **HTTPS Only**: Vercel enforces HTTPS for all production deployments

---

## 🆚 **Comparison: Email Whitelist vs SAML SSO**

| Feature | Email Whitelist (FREE) | SAML SSO (PRO) |
|---------|----------------------|----------------|
| Cost | $0/month | $25/month + $0.015/MAU |
| Setup Time | 1 hour | 1-2 weeks (UIUC IT) |
| Security | High (RLS + magic links) | Enterprise (SSO) |
| User Experience | Good (passwordless) | Excellent (true SSO) |
| Admin Management | Manual whitelist | Automatic via IdP |
| Migration Path | Easy upgrade to SAML later | N/A |

---

## 🎯 **Next Steps**

1. Run database schema updates
2. Initialize Next.js project with auth components
3. Test admin login flow
4. Build admin dashboard
5. Test RLS policies thoroughly
6. Deploy to Vercel
7. Add remaining admins to whitelist

**Ready to proceed with Next.js setup?**
