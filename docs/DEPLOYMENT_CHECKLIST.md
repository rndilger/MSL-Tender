# MSL-Tender Deployment Checklist

## Pre-Deployment Status

### ✅ Data Preparation (COMPLETE)
- [x] Consolidated 13 Excel files into single CSV (1,490 records)
- [x] Fixed study number mismatches
- [x] Cleaned database records without images (removed 261 records)
- [x] Achieved 1:1 database-to-image matching
- [x] Moved unmatched images to archive (312 images)
- [x] Staged 1,490 images for upload
- [x] Generated template for archived images

### ✅ Repository Setup (COMPLETE)
- [x] GitHub repository created (rndilger/MSL-Tender)
- [x] Project structure established
- [x] Database schema ready (`database/schema.sql`)
- [x] Documentation complete
- [x] .gitignore configured (sensitive data excluded)

---

## Deployment Steps

### 1. Supabase Setup

Follow: `docs/SUPABASE_SETUP_WALKTHROUGH.md`

- [ ] Create Supabase account (sign in with GitHub)
- [ ] Create new project: `msl-tender`
- [ ] Save database password securely
- [ ] Run database schema (`database/schema.sql`)
- [ ] Verify tables created (6 tables)
- [ ] Import data: `consolidated_data_latest.csv` → `pork_samples` table
- [ ] Verify: 1,490 records imported
- [ ] Create storage bucket: `pork-images` (public)
- [ ] Configure storage policies (public read)
- [ ] Copy API credentials:
  - Project URL
  - Anon (public) key
  - Service role key

**Status**: ⬜ Not Started

---

### 2. Image Upload

- [ ] Install Python package: `pip install supabase`
- [ ] Update `scripts/upload_images_to_supabase.py` with credentials
- [ ] Set environment variables:
  ```powershell
  $env:SUPABASE_URL = "https://xxxxx.supabase.co"
  $env:SUPABASE_SERVICE_ROLE_KEY = "your-key"
  ```
- [ ] Run upload script: `python scripts/upload_images_to_supabase.py`
- [ ] Verify: 1,490 images uploaded
- [ ] Update `sample_images` table with storage URLs
- [ ] Test: Access sample image URLs

**Status**: ⬜ Not Started

---

### 3. Code Handoff & Review

**Waiting on**: Lab member to provide codebase

- [ ] Receive codebase from lab member
- [ ] Review existing code structure
- [ ] Assess functionality completeness
- [ ] Document missing features
- [ ] Plan completion roadmap

**Status**: ⬜ Waiting on handoff

---

### 4. Local Development Setup

Once codebase is received:

- [ ] Review `package.json` dependencies
- [ ] Create `.env.local` with Supabase credentials:
  ```env
  NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
  NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
  ```
- [ ] Install dependencies: `npm install`
- [ ] Test local development: `npm run dev`
- [ ] Verify database connection
- [ ] Verify image loading
- [ ] Test core functionality

**Status**: ⬜ Not Started

---

### 5. Vercel Deployment

Follow: `docs/VERCEL_DEPLOYMENT_GUIDE.md`

- [ ] Create Vercel account (sign in with GitHub)
- [ ] Connect GitHub repository to Vercel
- [ ] Configure environment variables in Vercel:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] Configure build settings (auto-detect Next.js)
- [ ] Deploy to production
- [ ] Test production deployment
- [ ] Verify all functionality works
- [ ] Set up automatic deployments from `main` branch
- [ ] Configure preview deployments for PRs

**Status**: ⬜ Not Started

---

### 6. Testing & Verification

- [ ] Test user authentication flow
- [ ] Test experiment selection
- [ ] Test image viewing/evaluation
- [ ] Test response submission
- [ ] Test data export
- [ ] Verify mobile responsiveness
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Performance testing (image load times)
- [ ] Security review (RLS policies)

**Status**: ⬜ Not Started

---

### 7. Post-Deployment

- [ ] Configure custom domain (if applicable)
- [ ] Set up monitoring/analytics
- [ ] Document API endpoints
- [ ] Create user guide
- [ ] Train lab members on system usage
- [ ] Plan for archived images completion
- [ ] Schedule data backups

**Status**: ⬜ Not Started

---

## Critical Credentials to Save

Store securely (password manager, secure notes):

### Supabase
- [ ] Project URL: `https://xxxxx.supabase.co`
- [ ] Database Password: `_______________`
- [ ] Anon Key: `eyJhbG...` (public, safe to expose)
- [ ] Service Role Key: `eyJhbG...` (PRIVATE, never expose)

### Vercel
- [ ] Project URL: `https://msl-tender.vercel.app`
- [ ] Team/Account: Connected to GitHub (rndilger)

### GitHub
- [ ] Repository: `rndilger/MSL-Tender`
- [ ] Access: Connected to Vercel & Supabase

---

## Current Blockers

1. **Waiting on codebase handoff** from lab member
   - Need to assess current state
   - Need to plan completion strategy

---

## Next Immediate Actions

1. **You**: Create Supabase account and project
2. **You**: Run database schema
3. **You**: Import data CSV
4. **You**: Create storage bucket
5. **Me**: Help configure and test
6. **You**: Get codebase from lab member
7. **Both**: Code review and deployment

---

## Resources

- [Supabase Setup Walkthrough](./SUPABASE_SETUP_WALKTHROUGH.md)
- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT_GUIDE.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Database Schema](../database/schema.sql)
- [Upload Script](../scripts/upload_images_to_supabase.py)

---

## Questions?

Reach out when:
- Supabase account is created (need credentials)
- Database is imported (verify data)
- Images are uploaded (verify access)
- Codebase is received (start review)
- Ready for Vercel deployment
