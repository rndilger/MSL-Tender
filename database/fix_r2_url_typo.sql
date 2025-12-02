-- Fix typo in R2 URLs (843722 vs 8433722)
-- The correct URL from Cloudflare dashboard is: https://pub-54fd27572f2e4efc843722bee98239e0.r2.dev

-- Step 1: Check current URLs
SELECT 
  COUNT(*) as total,
  COUNT(CASE WHEN image_url LIKE '%8433722%' THEN 1 END) as wrong_url,
  COUNT(CASE WHEN image_url LIKE '%843722%' AND image_url NOT LIKE '%8433722%' THEN 1 END) as correct_url
FROM sample_images;

-- Step 2: Fix the typo
UPDATE sample_images
SET image_url = REPLACE(
  image_url,
  'https://pub-54fd27572f2e4efc8433722bee98239e0.r2.dev',
  'https://pub-54fd27572f2e4efc843722bee98239e0.r2.dev'
)
WHERE image_url LIKE '%8433722%';

-- Step 3: Verify fix
SELECT 
  COUNT(*) as total,
  COUNT(CASE WHEN image_url LIKE '%8433722%' THEN 1 END) as wrong_url,
  COUNT(CASE WHEN image_url LIKE '%843722%' AND image_url NOT LIKE '%8433722%' THEN 1 END) as correct_url
FROM sample_images;

-- Step 4: View sample of corrected URLs
SELECT id, image_type, image_url
FROM sample_images
LIMIT 5;
