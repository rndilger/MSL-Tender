# Supabase Setup Guide for Tender

This guide walks through setting up Supabase for the Tender application, following the same approach used in the Department 56 web app project.

## Prerequisites

- GitHub account (rndilger)
- Supabase account
- Vercel account

## Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in project details:
   - **Name**: Tender (or MSL-Tender)
   - **Database Password**: (generate strong password - save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Start with Free tier

## Step 2: Set Up Database Schema

1. In Supabase Dashboard, go to **SQL Editor**
2. Copy the contents of `database/schema.sql`
3. Paste and run the SQL script
4. Verify tables were created in **Table Editor**

Expected tables:
- `pork_samples`
- `experiments`
- `experiment_samples`
- `participant_sessions`
- `responses`
- `sample_images`

## Step 3: Import Consolidated Data

### Using Supabase Dashboard

1. Go to **Table Editor** → `pork_samples` table
2. Click **Insert** → **Import data from CSV**
3. Upload `database/consolidated_data_for_sql_[timestamp].csv`
4. Map CSV columns to database columns (should auto-match)
5. Click **Import**

### Using SQL (Alternative)

```sql
-- Create temporary table for import
CREATE TEMP TABLE temp_import (
    study_number INTEGER,
    original_chop_id INTEGER,
    standardized_chop_id TEXT,
    -- ... all columns from CSV
);

-- Copy from CSV (if using psql)
\COPY temp_import FROM 'consolidated_data_latest.csv' WITH CSV HEADER;

-- Insert into main table
INSERT INTO pork_samples (
    study_number,
    original_chop_id,
    standardized_chop_id,
    -- ... columns
)
SELECT 
    study_number,
    original_chop_id,
    standardized_chop_id,
    -- ... columns
FROM temp_import;
```

## Step 4: Set Up Storage for Images

1. In Supabase Dashboard, go to **Storage**
2. Create new bucket: `pork-images`
3. Set bucket to **Public** (for participant access)
4. Upload image files organized by study:
   ```
   pork-images/
   ├── 2003/
   ├── 2004/
   ├── 2006/
   └── ...
   ```

## Step 5: Get API Credentials

1. Go to **Settings** → **API**
2. Copy these values (you'll need them for Vercel):
   - **Project URL**: `https://[project-ref].supabase.co`
   - **Anon public key**: `eyJ...`
   - **Service role key**: `eyJ...` (keep secret!)

## Step 6: Connect to Vercel

### In Vercel Dashboard:

1. Import your GitHub repository: `rndilger/MSL-Tender`
2. Configure project:
   - **Framework Preset**: Next.js (or your chosen framework)
   - **Root Directory**: `frontend` (or leave as root)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (for Next.js)

### Environment Variables in Vercel:

Add these in **Settings** → **Environment Variables**:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[project-ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ... (for admin functions only)

# Optional: Environment
NODE_ENV=production
```

## Step 7: Enable Authentication (Optional)

For the admin dashboard:

1. In Supabase Dashboard, go to **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure email templates for invitations
4. Create admin users:
   - Go to **Authentication** → **Users**
   - Click **Invite User**
   - Enter researcher email addresses

## Step 8: Test Connection

Create a test file in your frontend:

```javascript
// test-connection.js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

async function testConnection() {
  const { data, error } = await supabase
    .from('pork_samples')
    .select('count')
    
  if (error) {
    console.error('Error:', error)
  } else {
    console.log('Connection successful!', data)
  }
}

testConnection()
```

## Step 9: Deploy

1. Push your code to GitHub
2. Vercel will automatically deploy
3. Check deployment logs for any errors
4. Test the live site

## Database Maintenance

### Regular Backups

Supabase automatically backs up your database. To download a backup:

1. Go to **Settings** → **Database**
2. Click **Download backup**

### Monitor Usage

1. Go to **Settings** → **Usage**
2. Check database size, bandwidth, storage

## Security Checklist

- [ ] RLS (Row Level Security) policies are enabled
- [ ] Service role key is only used server-side
- [ ] Anon key is only used client-side
- [ ] Image storage bucket has appropriate access policies
- [ ] Admin users are created with proper authentication
- [ ] Environment variables are set in Vercel (not in code)

## Helpful SQL Queries

### Check data import
```sql
SELECT 
    study_number, 
    COUNT(*) as count 
FROM pork_samples 
GROUP BY study_number 
ORDER BY study_number;
```

### View experiment statistics
```sql
SELECT * FROM experiment_participation;
```

### Check for missing data
```sql
SELECT 
    COUNT(*) FILTER (WHERE chop_color IS NULL) as missing_color,
    COUNT(*) FILTER (WHERE chop_marbling IS NULL) as missing_marbling,
    COUNT(*) FILTER (WHERE ph IS NULL) as missing_ph
FROM pork_samples;
```

## Troubleshooting

### Connection Issues
- Verify API keys are correct
- Check Supabase project status
- Ensure RLS policies allow access

### Import Errors
- Check CSV format matches schema
- Verify column names match exactly
- Look for data type mismatches

### Performance Issues
- Check indexes are created
- Monitor query performance in Supabase Dashboard
- Consider adding composite indexes for common queries

## Next Steps

1. Set up frontend application structure
2. Install Supabase client library: `npm install @supabase/supabase-js`
3. Create API utility functions
4. Build admin dashboard
5. Build consumer interface
6. Test end-to-end workflow

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Next.js + Supabase Guide](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)
