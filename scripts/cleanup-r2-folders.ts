import { S3Client, ListObjectsV2Command, DeleteObjectsCommand } from '@aws-sdk/client-s3';

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
  console.log(`\nDeleting folder: ${prefix}`);
  
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
      console.log(`No objects found in ${prefix}`);
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
    
    console.log(`Deleted ${objects.length} objects (total: ${totalDeleted})`);
    
    if (deleteResponse.Errors && deleteResponse.Errors.length > 0) {
      console.error('Errors during deletion:', deleteResponse.Errors);
    }
    
    continuationToken = listResponse.NextContinuationToken;
  } while (continuationToken);
  
  console.log(`Finished deleting ${prefix} - Total objects deleted: ${totalDeleted}`);
}

async function main() {
  console.log('R2 Cleanup Script');
  console.log('=================\n');
  
  // Delete the incorrectly created folders
  const foldersToDelete = [
    'photos/processed/',
    'processed/original/',
  ];
  
  for (const folder of foldersToDelete) {
    try {
      await deleteFolder(folder);
    } catch (error) {
      console.error(`Error deleting ${folder}:`, error);
    }
  }
  
  console.log('\nCleanup complete!');
}

main().catch(console.error);
