-- Fix R2 URLs in the new project (qmecfslaeadrfdxlcekk)
-- The correct URL is: https://pub-54fd27572f2e4efc843722bee98239e0.r2.dev
-- But the database was populated with: https://pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev

-- Show current URLs before update
SELECT 
    'Before Update' as status,
    COUNT(*) as total_images,
    image_url
FROM sample_images
GROUP BY image_url
LIMIT 5;

-- Update to correct R2 URL with /original/ path
UPDATE sample_images
SET image_url = REPLACE(
    image_url, 
    'https://pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev',
    'https://pub-54fd27572f2e4efc843722bee98239e0.r2.dev/original'
)
WHERE image_url LIKE '%pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev%';

-- Show updated URLs
SELECT 
    'After Update' as status,
    COUNT(*) as total_images,
    image_url
FROM sample_images
GROUP BY image_url
LIMIT 5;

-- Verify all images now have correct URL
SELECT COUNT(*) as images_with_correct_url
FROM sample_images
WHERE image_url LIKE '%pub-54fd27572f2e4efc843722bee98239e0.r2.dev/original/%';

SELECT COUNT(*) as images_with_wrong_url
FROM sample_images
WHERE image_url LIKE '%pub-f04b5ab9baba4bc98b9a24e87a73f8c5.r2.dev%';
