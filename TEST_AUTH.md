# Authentication Testing Guide

## Changes Made

### 1. Fixed `/app/auth/callback/route.ts`
**Problem**: Cookies weren't persisting through redirects
**Solution**: Inline createServerClient with direct cookie handling instead of using the helper function

### 2. Restored `/app/admin/dashboard/page.tsx`
**Change**: Removed hardcoded user ID bypass, restored proper `getUser()` check

## Testing Steps

1. **Clear all cookies** for localhost:3000 or the production domain
2. Go to `/admin/login`
3. Enter your email: `rdilger2@illinois.edu`
4. Click "Send Magic Link"
5. Check your email and click the link
6. You should land on `/admin/dashboard` and **stay there**

## What to Watch For

### Success Indicators:
- ✅ Clicking magic link takes you to dashboard
- ✅ Dashboard shows "Welcome, Ryan Dilger"
- ✅ Refreshing dashboard keeps you logged in
- ✅ No redirect loop back to login

### Failure Indicators:
- ❌ Redirected back to login page after clicking magic link
- ❌ Dashboard briefly appears then redirects to login
- ❌ Multiple redirects in browser history

## Debugging

If it still loops, check browser DevTools:

### Network Tab:
1. Click magic link
2. Watch the redirect chain:
   - Should see: `/auth/callback?code=...` → 302 to `/admin/dashboard` → 200
   - Bad: `/auth/callback` → `/admin/dashboard` → 302 to `/admin/login` (loop)

### Application Tab → Cookies:
After clicking magic link, you should see these cookies:
- `sb-<project-id>-auth-token`
- `sb-<project-id>-auth-token-code-verifier`

If cookies are missing, the session didn't persist.

### Console:
Any errors related to:
- "Failed to set cookie"
- "Invalid session"
- "No user found"

## Why This Should Work

The key change is in how we create the Supabase client in the callback route:

**Before** (broken):
```typescript
const supabase = await createClient() // Uses cookies() helper
await supabase.auth.exchangeCodeForSession(code)
return NextResponse.redirect(...)
// Cookies were set but NOT included in redirect response
```

**After** (fixed):
```typescript
const cookieStore = await cookies()
const supabase = createServerClient(..., {
  cookies: {
    setAll(cookiesToSet) {
      cookiesToSet.forEach(({ name, value, options }) =>
        cookieStore.set(name, value, options)
      )
    }
  }
})
await supabase.auth.exchangeCodeForSession(code)
return NextResponse.redirect(...)
// Cookies are set directly on the cookieStore before redirect
```

The middleware will then pick up these cookies and refresh the session on the next request.
