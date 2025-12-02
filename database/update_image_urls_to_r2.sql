-- ============================================
-- Update Image URLs from Supabase Storage to Cloudflare R2
-- ============================================
-- Run this AFTER confirming all images are uploaded to R2

-- Step 1: View current URLs to verify they need updating
SELECT 
  id, 
  image_type,
  image_url,
  CASE 
    WHEN image_url LIKE '%supabase%' THEN 'Supabase'
    WHEN image_url LIKE '%r2.dev%' THEN 'R2'
    ELSE 'Unknown'
  END as storage_provider
FROM sample_images
LIMIT 10;

-- Step 2: Count how many URLs need updating
SELECT 
  COUNT(*) as total_images,
  COUNT(CASE WHEN image_url LIKE '%supabase%' THEN 1 END) as supabase_urls,
  COUNT(CASE WHEN image_url LIKE '%r2.dev%' THEN 1 END) as r2_urls
FROM sample_images;

-- Step 3: Preview what the updated URLs will look like (DOESN'T CHANGE DATA)
SELECT 
  id,
  image_type,
  image_url as old_url,
  REPLACE(
    image_url,
    'https://vxqpbohiradglqfxwjco.supabase.co/storage/v1/object/public/pork-images',
    'https://pub-54fd27572f2e4efc8433722bee98239e0.r2.dev'
  ) as new_url
FROM sample_images
WHERE image_url LIKE '%supabase%'
LIMIT 5;

-- ============================================
-- IMPORTANT: Only run Step 4 after confirming:
-- 1. All 1,490 images uploaded successfully to R2
-- 2. You can access a few test images at the R2 URLs
-- 3. The preview URLs in Step 3 look correct
-- ============================================

-- Step 4: UPDATE all URLs from Supabase to R2
UPDATE sample_images
SET image_url = REPLACE(
  image_url,
  'https://vxqpbohiradglqfxwjco.supabase.co/storage/v1/object/public/pork-images',
  'https://pub-54fd27572f2e4efc8433722bee98239e0.r2.dev'
)
WHERE image_url LIKE '%supabase%';

-- Step 5: Verify the update was successful
SELECT 
  COUNT(*) as total_images,
  COUNT(CASE WHEN image_url LIKE '%supabase%' THEN 1 END) as supabase_urls,
  COUNT(CASE WHEN image_url LIKE '%r2.dev%' THEN 1 END) as r2_urls
FROM sample_images;

-- Step 6: View a few updated URLs to confirm
SELECT 
  id, 
  image_type, 
  image_url
FROM sample_images
LIMIT 10;

-- ============================================
-- Test Image Access (after Step 4)
-- ============================================
-- Copy a few image_url values from Step 6 and paste them
-- in your browser to confirm the images load from R2
