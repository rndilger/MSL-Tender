# Supabase Project Migration Guide

## Overview
This guide documents the process of migrating the MSL Tender application's Supabase project from a personal GitHub account (@rndpig) to a work GitHub account (@rndilger).

**Estimated Time:** 30-45 minutes  
**Risk Level:** Medium (requires careful coordination of credentials)  
**Rollback Option:** Keep old project active until new one is verified

---

## Pre-Migration Checklist

### Current State
- **Current Supabase Account:** GitHub @rndpig (personal)
- **Target Supabase Account:** GitHub @rndilger (work)
- **Current Project URL:** https://lqnxzgphdbowkzyphmqs.supabase.co
- **Database Contents:**
  - 1,490 pork_samples
  - 1,490 sample_images (URLs pointing to Cloudflare R2)
  - 1 admin_users record
  - 0 experiments
- **Storage:** 0 buckets (images stored in Cloudflare R2)
- **Auth Users:** 1 admin user (rdilger2@illinois.edu)

### Prerequisites
- [ ] Access to GitHub account @rndilger (work)
- [ ] Access to Supabase dashboard via GitHub @rndpig (personal)
- [ ] Access to Vercel dashboard
- [ ] Git commit access to repository
- [ ] Backup of all environment variables

---

## Migration Steps

### Phase 1: Export Current Project

#### 1.1 Export Database Schema
```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Login to Supabase CLI with current account
supabase login

# Link to current project
supabase link --project-ref lqnxzgphdbowkzyphmqs

# Export schema to SQL file
supabase db dump --schema public --data-only=false > database/migration_schema.sql

# Export data separately
supabase db dump --schema public --data-only=true > database/migration_data.sql
```

#### 1.2 Document Current Configuration
Create backup file with current settings:

```bash
# Save current environment variables
cp .env.local .env.local.backup

# Document current Supabase settings:
# - Project URL: https://lqnxzgphdbowkzyphmqs.supabase.co
# - Anon Key: (from current project settings)
# - Service Role Key: (from current project settings)
```

#### 1.3 Export RLS Policies
The following RLS policies are currently in place:

**admin_users table:**
- `anon_select`: Allows anonymous SELECT (for login whitelist check)
- `authenticated_select`: Allows authenticated users to read all records
- `authenticated_write`: Allows authenticated users full access

**pork_samples table:**
- Standard authenticated user policies

**sample_images table:**
- Standard authenticated user policies

These are already captured in `database/fix_rls_recursion.sql`.

---

### Phase 2: Create New Project

#### 2.1 Create Supabase Account
1. Go to https://supabase.com
2. Click "Sign in with GitHub"
3. Authenticate with GitHub @rndilger (work account)
4. Authorize Supabase to access your GitHub account

#### 2.2 Create New Project
1. Click "New Project"
2. Configure:
   - **Name:** msl-tender
   - **Database Password:** Generate strong password and save to password manager
   - **Region:** US East (closest to University of Illinois)
   - **Plan:** Free tier
3. Wait for project provisioning (2-3 minutes)

#### 2.3 Note New Project Details
Document the following from the new project:
- Project URL: `https://[NEW_PROJECT_REF].supabase.co`
- Anon Key: From Settings → API
- Service Role Key: From Settings → API
- Database Password: From password manager

---

### Phase 3: Import Data to New Project

#### 3.1 Link CLI to New Project
```bash
# Logout from old account
supabase logout

# Login with new account (will open browser for GitHub authentication)
# Authenticate with GitHub @rndilger when prompted
supabase login

# Link to new project
supabase link --project-ref [NEW_PROJECT_REF]
```

#### 3.2 Import Schema
```bash
# Apply schema to new project
supabase db push --file database/migration_schema.sql

# Verify schema was created
supabase db list
```

#### 3.3 Import Data
```bash
# Apply data to new project
supabase db push --file database/migration_data.sql
```

#### 3.4 Verify Data Migration
```bash
# Run verification script
python scripts/check_supabase_storage.py
```

Expected output:
- pork_samples: 1490 rows
- sample_images: 1490 rows
- admin_users: 1 row
- experiments: 0 rows

---

### Phase 4: Update Application Configuration

#### 4.1 Update Local Environment Variables
Edit `.env.local`:

```env
# Old values (keep commented for reference)
# NEXT_PUBLIC_SUPABASE_URL=https://lqnxzgphdbowkzyphmqs.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=old_anon_key
# SUPABASE_SERVICE_ROLE_KEY=old_service_key

# New values
NEXT_PUBLIC_SUPABASE_URL=https://[NEW_PROJECT_REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[new_anon_key]
SUPABASE_SERVICE_ROLE_KEY=[new_service_key]

# Cloudflare R2 credentials remain unchanged
R2_ACCOUNT_ID=[existing_value]
R2_ACCESS_KEY_ID=[existing_value]
R2_SECRET_ACCESS_KEY=[existing_value]
R2_BUCKET_NAME=msl-tender-images
R2_PUBLIC_URL=https://pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev
```

#### 4.2 Update Vercel Environment Variables
1. Go to Vercel dashboard: https://vercel.com/rndpigs-projects
2. Navigate to msl-tender project → Settings → Environment Variables
3. Update the following for **Production**, **Preview**, and **Development**:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
4. Click "Save"

#### 4.3 Redeploy Application
```bash
# Commit environment variable reference update (not actual secrets)
git add .env.local.example  # If you maintain this file
git commit -m "docs: Update Supabase project reference for work account migration"
git push origin main

# Vercel will automatically redeploy with new environment variables
```

---

### Phase 5: Verification and Testing

#### 5.1 Test Authentication
1. Navigate to production URL: https://msl-tender.vercel.app/admin/login
2. Attempt login with rdilger2@illinois.edu
3. Verify successful authentication
4. Confirm redirect to dashboard

#### 5.2 Verify Data Display
1. Check dashboard stats:
   - Sample Count: 1490
   - Experiments: 0
   - Admin User: rdilger2@illinois.edu
2. Navigate to Sample Browser
3. Verify images load from Cloudflare R2
4. Spot-check several sample records for correct data

#### 5.3 Test Database Operations
```bash
# Run test query to verify RLS policies
python scripts/check_admin_users.py
```

Expected: Should show 1 admin user with rdilger2@illinois.edu

#### 5.4 Verify Cloudflare R2 Integration
- Confirm sample images display correctly
- Check that R2 URLs are unchanged (sample_images table stores full URLs)
- No changes needed to R2 configuration

---

### Phase 6: Cleanup

#### 6.1 Keep Old Project (Recommended)
**Option A: Maintain as backup for 30 days**
- Leave old Supabase project active
- Monitor new project for stability
- After 30 days of successful operation, delete old project

#### 6.2 Update Documentation
- [ ] Update README.md with new Supabase project reference
- [ ] Update any developer onboarding docs
- [ ] Document this migration in project history

#### 6.3 Archive Old Credentials
```bash
# Move old backup to archive folder
mkdir -p docs/archives
mv .env.local.backup docs/archives/.env.local.backup.$(date +%Y%m%d)
```

---

## Rollback Plan

If issues arise during or after migration:

### Immediate Rollback (During Migration)
1. Revert `.env.local` to backed up version:
   ```bash
   cp .env.local.backup .env.local
   ```
2. Revert Vercel environment variables to old values
3. Redeploy: `git commit --allow-empty -m "Rollback" && git push`

### Post-Migration Rollback
1. Access Vercel dashboard
2. Find the deployment before the migration
3. Click "Promote to Production"
4. Update environment variables back to old project
5. Investigate issues in new project without time pressure

---

## Troubleshooting

### Issue: Authentication fails on new project
**Cause:** Admin user not properly migrated  
**Solution:**
```sql
-- In new Supabase SQL Editor
INSERT INTO admin_users (id, email, role, active)
VALUES 
  ('[NEW_AUTH_USER_ID]', 'rdilger2@illinois.edu', 'super_admin', true);
```

### Issue: RLS policies blocking access
**Cause:** Policies not properly recreated  
**Solution:** Re-run `database/fix_rls_recursion.sql` in new project

### Issue: Images not loading
**Cause:** Cloudflare R2 URLs should be unaffected  
**Solution:** Verify sample_images table contains correct R2 URLs:
```sql
SELECT image_url FROM sample_images LIMIT 5;
```

### Issue: Vercel build fails
**Cause:** Environment variables not updated  
**Solution:** Double-check all three environment scopes (Production, Preview, Development) in Vercel settings

---

## Post-Migration Enhancements

Once migration is complete and verified, consider:

1. **Organization Setup:** Create a Supabase organization for the Dilger Lab to enable future project transfers
2. **Team Access:** Add other lab members as collaborators
3. **Database Backups:** Set up automated daily backups via Supabase Pro plan (if budget allows)
4. **Monitoring:** Configure Supabase alerts for auth failures, database errors

---

## Migration Timeline

**Recommended Schedule:**
- **Day 0 (Today):** Review documentation, prepare credentials
- **Day 1:** Execute Phases 1-3 (export and import, 15 minutes)
- **Day 1:** Execute Phase 4 (update configs, 10 minutes)
- **Day 1:** Execute Phase 5 (testing, 15 minutes)
- **Day 30:** Execute Phase 6 cleanup (delete old project)

---

## Notes

- Cloudflare R2 storage is completely independent and requires no changes
- Sample images table stores full R2 URLs, so no path updates needed
- Current phantom storage quota issue (3.524GB) will not transfer to new project
- Authentication architecture (password-based) remains unchanged
- All RLS policies and database schema are preserved

---

## Contact and Support

If issues arise:
1. Check Supabase status: https://status.supabase.com
2. Supabase Discord: https://discord.supabase.com
3. Vercel support: https://vercel.com/support
4. GitHub Issues: Create issue in repository for team visibility

---

**Document Version:** 1.0  
**Created:** December 2, 2024  
**Author:** Ryan Dilger  
**Last Updated:** December 2, 2024
