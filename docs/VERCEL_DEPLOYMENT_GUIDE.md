# Vercel Deployment Guide

## Overview
Vercel is the optimal platform for deploying Next.js applications with zero-config deployments, automatic HTTPS, and global CDN.

## Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

## Step 2: Create Vercel Account & Link Project

1. Go to [https://vercel.com](https://vercel.com)
2. Sign up/in with your GitHub account (rndilger)
3. You'll link the repository in the next steps

## Step 3: Prepare Your Project

### A. Create `vercel.json` Configuration

The project needs a `vercel.json` file in the root (we'll create this together once we have the codebase).

Typical configuration:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

### B. Configure Environment Variables

In your project, environment variables will be needed:
- Development: `.env.local` (local only)
- Production: Set in Vercel Dashboard

## Step 4: Deploy via GitHub Integration (Recommended)

### A. Connect Repository

1. Go to Vercel Dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository:
   - Select `rndilger/MSL-Tender`
4. Configure Project:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `./` (or wherever package.json is)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

### B. Set Environment Variables

In Vercel project settings:
1. Go to **Settings** → **Environment Variables**
2. Add each variable for **Production**, **Preview**, and **Development**:

```
NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbG...
```

**Do NOT add**:
- `SUPABASE_SERVICE_ROLE_KEY` (keep server-side only)
- Any secrets that shouldn't be in client-side code

### C. Deploy

1. Click "Deploy"
2. Vercel will:
   - Clone your repo
   - Install dependencies
   - Build the Next.js app
   - Deploy to global CDN
3. Get your URL: `https://msl-tender.vercel.app` (or similar)

## Step 5: Configure Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your domain (e.g., `tender.msl.illinois.edu`)
3. Follow DNS configuration instructions
4. Vercel automatically provisions SSL certificate

## Step 6: Automatic Deployments

Once connected to GitHub:
- **Push to `main`** → Deploys to Production
- **Push to other branches** → Creates Preview deployment
- **Pull Requests** → Automatic preview URLs

## Step 7: Vercel CLI Deployment (Alternative)

If you prefer CLI over GitHub integration:

```powershell
# Login to Vercel
vercel login

# Navigate to project
cd "c:\Users\rndpi\Documents\Coding Projects\MSL-tender"

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Step 8: Configure Build Settings

### Optimize for Performance

In `next.config.js` (or `next.config.mjs`):

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['xxxxx.supabase.co'], // Your Supabase project URL
    formats: ['image/avif', 'image/webp'],
  },
  // Enable React strict mode
  reactStrictMode: true,
  // Optimize production builds
  swcMinify: true,
  // Configure redirects if needed
  async redirects() {
    return [
      {
        source: '/',
        destination: '/experiments',
        permanent: false,
      },
    ]
  },
}

module.exports = nextConfig
```

## Step 9: Monitor Deployment

1. **View Logs**: Vercel Dashboard → Your Project → Deployments
2. **Check Build Logs**: Click on any deployment
3. **Runtime Logs**: Available in real-time
4. **Analytics**: Enable Vercel Analytics for insights

## Step 10: Set Up Preview Deployments

Each git branch and PR gets a unique URL:
- `main` → `https://msl-tender.vercel.app`
- `feature-branch` → `https://msl-tender-git-feature-branch.vercel.app`
- PR #5 → `https://msl-tender-pr5.vercel.app`

---

## Deployment Checklist

Before first deployment:

- [ ] Supabase project created and configured
- [ ] Database schema deployed
- [ ] Data imported (1,490 records)
- [ ] Images uploaded to Supabase Storage
- [ ] Environment variables configured in Vercel
- [ ] GitHub repository connected to Vercel
- [ ] `package.json` has correct build scripts
- [ ] `.env.local` in `.gitignore`
- [ ] Test deployment successful

---

## Common Issues & Solutions

### Build Failures

**Issue**: Missing dependencies
```
Module not found: Can't resolve '@supabase/supabase-js'
```
**Solution**: Ensure `package.json` includes all dependencies:
```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.x.x",
    "next": "^14.x.x",
    "react": "^18.x.x"
  }
}
```

**Issue**: Environment variables not found
```
Error: NEXT_PUBLIC_SUPABASE_URL is not defined
```
**Solution**: Add variables in Vercel Dashboard → Settings → Environment Variables

### Runtime Errors

**Issue**: CORS errors accessing Supabase
**Solution**: 
1. Check Supabase URL in environment variables
2. Verify anon key is correct
3. Check RLS policies allow public read

**Issue**: Images not loading
**Solution**:
1. Add Supabase domain to `next.config.js` → `images.domains`
2. Verify storage bucket is public
3. Check image URLs are correct

### Performance Issues

**Issue**: Slow image loading
**Solution**:
- Use Next.js `<Image>` component with optimization
- Enable AVIF/WebP formats
- Implement lazy loading

**Issue**: Large bundle size
**Solution**:
- Use dynamic imports: `const Component = dynamic(() => import('./Component'))`
- Enable code splitting
- Analyze bundle: `npm run build && npm run analyze`

---

## Next Steps After Deployment

1. ✅ Test all functionality in production
2. ✅ Set up monitoring (Vercel Analytics, Sentry)
3. ✅ Configure custom domain
4. ✅ Enable preview deployments for team review
5. ✅ Set up CI/CD for automated testing

---

## Useful Vercel Commands

```powershell
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs [deployment-url]

# Remove deployment
vercel rm [deployment-name]

# Pull environment variables
vercel env pull .env.local

# Link local project to Vercel
vercel link
```

---

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Supabase + Vercel Integration](https://supabase.com/docs/guides/integrations/vercel)
