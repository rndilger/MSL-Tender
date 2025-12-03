# Fix Supabase Redirect URL Configuration

## Problem
The magic link is being generated, but Supabase is not redirecting to `/auth/callback` properly because the URL is not in the allowed list.

## Solution
Add the callback URL to Supabase's allowed redirect URLs:

### Steps:

1. Go to https://supabase.com/dashboard
2. Select your project: `vxqpbohiradglqfxwjco`
3. Go to **Authentication** → **URL Configuration**
4. Find the section **Redirect URLs**
5. Add these URLs to the allowed list:
   ```
   https://msl-tender.vercel.app/auth/callback
   http://localhost:3000/auth/callback
   ```
6. Click **Save**

### Current Redirect URL in Code:
The login page is setting:
```typescript
emailRedirectTo: `${redirectUrl}/auth/callback`
```

Where `redirectUrl` comes from `process.env.NEXT_PUBLIC_SITE_URL` or `window.location.origin`

### Expected Flow:
1. User clicks magic link → `vxqpbohiradglqfxwjco.supabase.co/auth/v1/verify?token=...&redirect_to=https://msl-tender.vercel.app/auth/callback`
2. Supabase verifies token
3. Supabase redirects to `https://msl-tender.vercel.app/auth/callback?code=...`
4. Callback route exchanges code for session
5. Callback redirects to `/admin/dashboard`

### Current Behavior (broken):
The redirect from Supabase to our callback might be failing because the URL isn't whitelisted, causing Supabase to redirect to a default URL or nowhere at all.

## After Adding URLs:
1. Clear browser cookies
2. Request new magic link
3. Click link in email
4. Should redirect properly through: Supabase → callback → dashboard
