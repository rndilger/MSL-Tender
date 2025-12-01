# Vercel Deployment Guide - Updated for MSL-Tender Next.js App

Complete guide for deploying the MSL-Tender production application to Vercel.

## 📋 Prerequisites

✅ **Before deploying, ensure you have:**
- Supabase project with auth schema deployed (`database/auth_schema.sql`)
- Next.js app built and tested locally (`npm run dev` in `app/` folder)
- GitHub repository with latest code pushed
- Vercel account (sign up at https://vercel.com with GitHub)
- Supabase project URL and anon key ready

---

## 🚀 Deployment Methods

### **Option 1: GitHub Integration (Recommended)**

Automatic deployments on every push to main branch.

#### Step 1: Push Latest Code

```powershell
cd "c:\Users\rndpi\Documents\Coding Projects\MSL-tender"
git add .
git commit -m "Add Next.js production app with authentication"
git push origin main
```

#### Step 2: Import to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select `rndilger/MSL-Tender` repository
4. **Important**: Set "Root Directory" to `app` (not the repo root)
5. Framework Preset: Next.js (should auto-detect)
6. Click "Deploy"

#### Step 3: Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables, add:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://vxqpbohiradglqfxwjco.supabase.co` | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key | Production, Preview, Development |
| `NEXT_PUBLIC_SITE_URL` | Your Vercel URL (e.g., `https://msl-tender.vercel.app`) | Production |

**Get anon key from**: https://supabase.com/dashboard/project/vxqpbohiradglqfxwjco/settings/api

#### Step 4: Redeploy with Environment Variables

After adding env vars:
1. Go to Deployments tab
2. Click "..." on latest deployment
3. Click "Redeploy"

---

### **Option 2: Vercel CLI (Alternative)**

Manual deployment via command line.

#### Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

#### Step 2: Login to Vercel

```powershell
vercel login
```

Follow prompts to authenticate with GitHub.

#### Step 3: Deploy from App Directory

```powershell
cd "c:\Users\rndpi\Documents\Coding Projects\MSL-tender\app"
vercel
```

Follow prompts:
- Set up and deploy? **Yes**
- Which scope? **Your personal account**
- Link to existing project? **No** (first time) or **Yes** (subsequent)
- Project name? **msl-tender** (or your choice)
- Directory? **.**
- Override settings? **No**

#### Step 4: Add Environment Variables

```powershell
# Add Supabase URL
vercel env add NEXT_PUBLIC_SUPABASE_URL

# Add Supabase anon key
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY

# Add site URL (use your production URL)
vercel env add NEXT_PUBLIC_SITE_URL
```

Choose environment: **Production, Preview, and Development**

#### Step 5: Deploy to Production

```powershell
vercel --prod
```

---

## 🔧 Project Configuration

### Root Directory Setting

**Critical**: Vercel must build from the `app/` subdirectory, not the repository root.

In Vercel Dashboard:
1. Project Settings → General
2. Root Directory: `app`
3. Save

### Build Settings

Vercel auto-detects Next.js projects. Default settings:
- **Framework**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### Domain Configuration

#### Custom Domain (Optional)

If you have `tender.msl.illinois.edu`:

1. Vercel Dashboard → Project → Settings → Domains
2. Add domain: `tender.msl.illinois.edu`
3. Add DNS records at your domain provider:
   - Type: `CNAME`
   - Name: `tender.msl` or `@`
   - Value: `cname.vercel-dns.com`
4. Wait for DNS propagation (5-60 minutes)

#### Default Vercel Domain

Your app will be available at:
- `https://msl-tender.vercel.app` (or similar)
- `https://msl-tender-rndilger.vercel.app`

---

## 🔐 Environment Variables Reference

### Required Variables

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://vxqpbohiradglqfxwjco.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...your-key-here

# Site Configuration (use your Vercel URL)
NEXT_PUBLIC_SITE_URL=https://msl-tender.vercel.app
```

### How to Get Values

**Supabase URL & Anon Key**:
1. Go to https://supabase.com/dashboard
2. Select your project (vxqpbohiradglqfxwjco)
3. Settings → API
4. Copy "Project URL" and "anon/public" key

**Site URL**:
- Development: `http://localhost:3000`
- Production: Your Vercel deployment URL

---

## ✅ Post-Deployment Checklist

After first deployment:

### 1. Test Authentication Flow
- [ ] Visit `/admin/login`
- [ ] Enter @illinois.edu email
- [ ] Receive magic link email
- [ ] Click link and verify redirect to dashboard
- [ ] Check middleware protection (try accessing `/admin/dashboard` without login)

### 2. Verify Supabase Connection
- [ ] Dashboard shows correct sample count (1,490)
- [ ] No console errors about Supabase connection
- [ ] RLS policies working (can't access other admin data)

### 3. Test Routes
- [ ] Root `/` redirects to `/admin/dashboard`
- [ ] `/admin/login` loads correctly
- [ ] `/admin/dashboard` protected (requires auth)
- [ ] Sign out works (redirects to login)

### 4. Check Environment Variables
- [ ] No `undefined` errors in console
- [ ] Supabase URL resolving correctly
- [ ] Images loading from Supabase Storage

### 5. Create First Admin
- [ ] Sign up with @illinois.edu email
- [ ] Get UUID from Supabase Dashboard → Auth → Users
- [ ] Run SQL to add to `admin_users` table:
```sql
INSERT INTO admin_users (id, email, full_name, role, is_active)
VALUES ('YOUR-UUID', 'your.email@illinois.edu', 'Your Name', 'super_admin', true);
```
- [ ] Test login again - should work!

---

## 🔄 Continuous Deployment

### Automatic Deployments

With GitHub integration:
1. Push to `main` branch → Production deployment
2. Push to other branches → Preview deployment
3. Pull requests → Preview deployment with unique URL

### Manual Redeployment

If you need to redeploy without code changes:
1. Vercel Dashboard → Deployments
2. Click "..." on deployment
3. Click "Redeploy"

### Branch Previews

Every branch gets a preview URL:
- `https://msl-tender-git-branch-name.vercel.app`

Perfect for testing before merging to main.

---

## 🐛 Troubleshooting

### Build Fails: "Cannot find module '@supabase/ssr'"

**Solution**: Ensure `app/package.json` has all dependencies:
```powershell
cd app
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs @supabase/ssr
```
Push changes and redeploy.

### "Invalid Supabase URL" Error

**Check**:
1. Environment variable is named `NEXT_PUBLIC_SUPABASE_URL` (with underscore)
2. Value includes `https://` protocol
3. No trailing slash
4. Environment is set for "Production"

**Fix**: Update env var in Vercel Dashboard → Settings → Environment Variables

### Redirect Loop at `/admin/dashboard`

**Cause**: Middleware can't verify admin status

**Check**:
1. Supabase anon key is correct
2. `admin_users` table exists
3. Your user UUID is in `admin_users` table
4. `is_active = true`

### Magic Links Not Working in Production

**Check Supabase Auth Settings**:
1. Supabase Dashboard → Authentication → URL Configuration
2. Add your Vercel URL to "Redirect URLs":
   - `https://msl-tender.vercel.app/admin/dashboard`
   - `https://msl-tender.vercel.app/**` (wildcard)
3. Save and test again

### Images Not Loading

**Check Storage URL**:
- Images: `https://vxqpbohiradglqfxwjco.supabase.co/storage/v1/object/public/pork-images/original/[filename].jpg`
- Bucket is public
- RLS policies allow public read

### Environment Variables Not Updating

**Solution**:
1. Update env vars in Vercel Dashboard
2. Redeploy (builds are cached)
3. Hard refresh browser (Ctrl+Shift+R)

---

## 📊 Monitoring & Analytics

### Vercel Analytics (Free)

Enable in Project Settings → Analytics:
- Page views
- Top pages
- Traffic sources
- Web Vitals (performance)

### Supabase Logs

Monitor database activity:
1. Supabase Dashboard → Logs
2. View auth events, queries, errors

### Error Tracking

Check runtime errors:
- Vercel Dashboard → Deployments → Click deployment → "Functions" tab
- View serverless function logs

---

## 🚀 Performance Optimization

### Image Optimization

Use Next.js Image component for pork chop images:
```tsx
import Image from 'next/image'

<Image
  src={imageUrl}
  alt="Pork chop"
  width={300}
  height={300}
  priority={false}
/>
```

### Edge Runtime

For faster admin dashboard:
```tsx
// app/admin/dashboard/page.tsx
export const runtime = 'edge'
```

### Caching Strategy

Static pages cached at CDN edge:
- `/admin/login` - Static, cached
- `/admin/dashboard` - Dynamic, revalidated
- `/survey/[id]` - Dynamic, ISR (Incremental Static Regeneration)

---

## 💰 Cost Estimates

### Vercel (Free Tier)
- **Included**:
  - 100 GB bandwidth/month
  - Unlimited serverless function executions
  - Automatic HTTPS
  - Preview deployments
  - Web Analytics
- **Cost**: $0/month

### Vercel Pro (If Needed)
- **Includes**:
  - 1 TB bandwidth
  - Advanced analytics
  - Password protection
  - Team collaboration
- **Cost**: $20/month per user

### Supabase (Free Tier - Current)
- **Included**:
  - 500 MB database
  - 1 GB file storage
  - 2 GB bandwidth
  - 50,000 monthly active users
- **Cost**: $0/month

**Total Monthly Cost**: $0 (free tier sufficient for MSL-Tender)

---

## 🔒 Security Best Practices

### Environment Variables
- ✅ Never commit `.env.local` to Git (already in `.gitignore`)
- ✅ Use Vercel env vars for production
- ✅ Rotate Supabase keys if exposed

### HTTPS
- ✅ Automatic via Vercel
- ✅ Enforced on all routes

### Content Security Policy
Add to `next.config.js` (optional):
```js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}
```

---

## 📝 Next Steps After Deployment

1. **Test thoroughly** - Run through entire auth flow
2. **Add admins** - Whitelist additional @illinois.edu users
3. **Build sample browser** - Next development phase
4. **Create first experiment** - Test workflow end-to-end
5. **Share preview** - Get feedback from team

---

## 🆘 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **Supabase + Vercel**: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs
- **This Project**: `app/README.md`

---

**Deployment Status**: Ready to deploy!
**Estimated Time**: 15-30 minutes for first deployment
**Difficulty**: Beginner-friendly with step-by-step guide

🚀 **Ready to deploy? Follow Option 1 (GitHub Integration) for the smoothest experience!**
