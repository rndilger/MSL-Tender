-- Fix image URLs: Change .jpg to .JPG (R2 is case-sensitive)
-- The actual files in R2 use uppercase .JPG extension

-- Show sample URLs before update
SELECT 
    'Before Update' as status,
    image_url
FROM sample_images
WHERE image_url LIKE '%.jpg'
LIMIT 5;

-- Count images with lowercase .jpg
SELECT COUNT(*) as images_needing_update
FROM sample_images
WHERE image_url LIKE '%.jpg';

-- Update .jpg to .JPG
UPDATE sample_images
SET image_url = REPLACE(image_url, '.jpg', '.JPG')
WHERE image_url LIKE '%.jpg';

-- Show sample URLs after update
SELECT 
    'After Update' as status,
    image_url
FROM sample_images
LIMIT 5;

-- Verify all images now have uppercase extension
SELECT 
    COUNT(*) as images_with_uppercase_JPG
FROM sample_images
WHERE image_url LIKE '%.JPG';

SELECT 
    COUNT(*) as images_with_lowercase_jpg
FROM sample_images
WHERE image_url LIKE '%.jpg';

-- Show a sample of the corrected URLs
SELECT 
    sample_id,
    image_url
FROM sample_images
ORDER BY sample_id
LIMIT 10;
