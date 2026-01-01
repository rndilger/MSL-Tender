import { S3Client, ListObjectsV2Command, DeleteObjectsCommand } from '@aws-sdk/client-s3';
import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

const R2_ACCOUNT_ID = process.env.R2_ACCOUNT_ID!;
const R2_ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID!;
const R2_SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY!;
const R2_BUCKET_NAME = process.env.R2_BUCKET_NAME!;

const r2Client = new S3Client({
  region: 'auto',
  endpoint: `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

async function deleteFolder(prefix: string) {
  console.log(`[R2 Cleanup] Deleting folder: ${prefix}`);
  
  let continuationToken: string | undefined;
  let totalDeleted = 0;
  
  do {
    // List objects in the folder
    const listCommand = new ListObjectsV2Command({
      Bucket: R2_BUCKET_NAME,
      Prefix: prefix,
      MaxKeys: 1000,
      ContinuationToken: continuationToken,
    });
    
    const listResponse = await r2Client.send(listCommand);
    
    if (!listResponse.Contents || listResponse.Contents.length === 0) {
      console.log(`[R2 Cleanup] No objects found in ${prefix}`);
      break;
    }
    
    // Delete objects in batches of 1000
    const objects = listResponse.Contents.map(obj => ({ Key: obj.Key! }));
    
    const deleteCommand = new DeleteObjectsCommand({
      Bucket: R2_BUCKET_NAME,
      Delete: {
        Objects: objects,
        Quiet: false,
      },
    });
    
    const deleteResponse = await r2Client.send(deleteCommand);
    totalDeleted += objects.length;
    
    console.log(`[R2 Cleanup] Deleted ${objects.length} objects (total: ${totalDeleted})`);
    
    if (deleteResponse.Errors && deleteResponse.Errors.length > 0) {
      console.error('[R2 Cleanup] Errors during deletion:', deleteResponse.Errors);
    }
    
    continuationToken = listResponse.NextContinuationToken;
  } while (continuationToken);
  
  return totalDeleted;
}

export async function POST() {
  try {
    const supabase = await createClient();
    
    // Check authentication
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    console.log('[R2 Cleanup] Starting cleanup...');
    
    // Delete the incorrectly created folders
    const foldersToDelete = [
      'photos/processed/',
      'processed/original/',
    ];
    
    const results: Record<string, number> = {};
    
    for (const folder of foldersToDelete) {
      try {
        const deleted = await deleteFolder(folder);
        results[folder] = deleted;
      } catch (error) {
        console.error(`[R2 Cleanup] Error deleting ${folder}:`, error);
        results[folder] = -1;
      }
    }
    
    console.log('[R2 Cleanup] Cleanup complete!', results);
    
    return NextResponse.json({
      message: 'Cleanup complete',
      results
    });
  } catch (error) {
    console.error('[R2 Cleanup] Error:', error);
    return NextResponse.json({ 
      error: 'Failed to cleanup R2',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
