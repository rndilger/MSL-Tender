# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign in with your GitHub account (rndilger)
3. Click "New Project"
4. Configure:
   - **Organization**: Select or create one
   - **Project Name**: `msl-tender` (or `MSL-Tender`)
   - **Database Password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
   - **Pricing Plan**: Free tier is fine to start
5. Click "Create new project" (takes ~2 minutes)

## Step 2: Configure Database

### A. Run Schema SQL

1. In Supabase Dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the entire contents of `database/schema.sql` from your project
4. Paste and click "Run"
5. Verify tables created: Go to **Table Editor** and check for:
   - `experiments`
   - `pork_samples`
   - `participant_sessions`
   - `responses`
   - `sample_images`
   - `experiment_samples`

### B. Import Data

1. Go to **Table Editor** → `pork_samples`
2. Click "Insert" → "Import data from CSV"
3. Upload `database/consolidated_data_latest.csv`
4. Map columns (should auto-detect)
5. Click "Import"
6. Verify: Should see 1,490 rows

## Step 3: Configure Storage

### A. Create Storage Bucket

1. Go to **Storage** in left sidebar
2. Click "Create a new bucket"
3. Configure:
   - **Name**: `pork-images`
   - **Public**: ✅ Yes (images need to be publicly accessible)
   - **File size limit**: 50 MB
   - **Allowed MIME types**: `image/jpeg,image/jpg,image/png`
4. Click "Create bucket"

### B. Set Storage Policies

1. Click on `pork-images` bucket
2. Go to **Policies** tab
3. Click "New Policy"
4. **For Public Read Access**:
   ```sql
   CREATE POLICY "Public read access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'pork-images');
   ```
5. Click "Review" → "Save"

6. **For Authenticated Upload** (optional for admin):
   ```sql
   CREATE POLICY "Authenticated users can upload"
   ON storage.objects FOR INSERT
   TO authenticated
   WITH CHECK (bucket_id = 'pork-images');
   ```

### C. Upload Images

**Option 1: Using Supabase Dashboard (for smaller batches)**
1. Go to Storage → `pork-images` bucket
2. Click "Upload files"
3. Select files from `photos_staged_for_upload/`
4. Upload (may need to do in batches)

**Option 2: Using Upload Script (recommended for 1,490 images)**
- We'll create a Python script for bulk upload after getting API keys

## Step 4: Get API Credentials

1. Go to **Project Settings** (gear icon)
2. Click **API** in left menu
3. Copy and save these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbG...` (long token)
   - **service_role key**: `eyJhbG...` (DO NOT expose publicly)

## Step 5: Configure Row Level Security (RLS)

The schema already includes RLS policies, but verify:

1. Go to **Authentication** → **Policies**
2. Check each table has appropriate policies:
   - `pork_samples`: Public read, admin write
   - `experiments`: Public read, admin write
   - `responses`: User can read/write their own
   - `participant_sessions`: User can read/write their own

## Step 6: Test Connection

We'll create a test script to verify:
- Database connection works
- Can query pork_samples
- Can access images in storage

---

## Next Steps After Setup

1. ✅ Create environment variables file (`.env.local`)
2. ✅ Test database queries
3. ✅ Upload all images via script
4. ✅ Link sample_images table to storage URLs
5. ✅ Set up Vercel deployment

---

## Troubleshooting

### Database Import Issues
- **Column mismatch**: Verify CSV headers match schema exactly
- **Data type errors**: Check for invalid values in numeric columns
- **Import timeout**: Use smaller batches or SQL INSERT script

### Storage Issues
- **403 errors**: Check bucket policies are set to public
- **CORS errors**: Add your domain to allowed origins in Storage settings
- **File size**: Verify images are under bucket size limit

### Connection Issues
- **Invalid API key**: Regenerate from Project Settings
- **Network errors**: Check project region and status
- **RLS blocking queries**: Verify policies match your use case

---

## Environment Variables Template

Create `.env.local` in your project root:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**⚠️ IMPORTANT**: Add `.env.local` to `.gitignore` (already done)
