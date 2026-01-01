import sharp from 'sharp';

interface CropCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

/**
 * Detect chop boundaries using GrabCut-inspired approach
 * Uses initial color-based mask then refines with morphological operations
 */
export async function detectChopBoundaries(imageUrl: string): Promise<CropCoordinates> {
  try {
    // Download the image
    const response = await fetch(imageUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.statusText}`);
    }
    
    const imageBuffer = Buffer.from(await response.arrayBuffer());
    
    // Get image metadata
    const image = sharp(imageBuffer);
    const metadata = await image.metadata();
    const width = metadata.width!;
    const height = metadata.height!;
    
    // Convert to raw RGB pixel data
    const { data } = await image
      .raw()
      .ensureAlpha()
      .toBuffer({ resolveWithObject: true });
    
    // Create initial trimap: definite background (0), possible foreground (128), definite foreground (255)
    const trimap = new Uint8Array(width * height);
    
    // Initialize with probable background
    trimap.fill(0);
    
    // Mark non-blue pixels as probable foreground
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        const r = data[idx];
        const g = data[idx + 1];
        const b = data[idx + 2];
        
        // Very conservative blue detection - only mark obvious blue as background
        const isDefiniteBlue = b > 140 && b > r + 30 && b > g + 25;
        
        if (!isDefiniteBlue) {
          trimap[y * width + x] = 128; // Probable foreground
        }
      }
    }
    
    // Erode the probable foreground to find definite foreground (core chop region)
    const definite_fg = new Uint8Array(width * height);
    const erodeKernel = 15;
    const erodeRadius = Math.floor(erodeKernel / 2);
    
    for (let y = erodeRadius; y < height - erodeRadius; y++) {
      for (let x = erodeRadius; x < width - erodeRadius; x++) {
        let allForeground = true;
        for (let dy = -erodeRadius; dy <= erodeRadius; dy++) {
          for (let dx = -erodeRadius; dx <= erodeRadius; dx++) {
            if (trimap[(y + dy) * width + (x + dx)] !== 128) {
              allForeground = false;
              break;
            }
          }
          if (!allForeground) break;
        }
        if (allForeground) {
          definite_fg[y * width + x] = 1;
        }
      }
    }
    
    // Find connected components of definite foreground
    const labels = new Int32Array(width * height);
    let currentLabel = 1;
    const componentSizes = new Map<number, number>();
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        if (definite_fg[y * width + x] === 1 && labels[y * width + x] === 0) {
          const stack = [[x, y]];
          let componentSize = 0;
          
          while (stack.length > 0) {
            const [cx, cy] = stack.pop()!;
            if (cx < 0 || cx >= width || cy < 0 || cy >= height) continue;
            if (labels[cy * width + cx] !== 0 || definite_fg[cy * width + cx] !== 1) continue;
            
            labels[cy * width + cx] = currentLabel;
            componentSize++;
            
            stack.push([cx + 1, cy]);
            stack.push([cx - 1, cy]);
            stack.push([cx, cy + 1]);
            stack.push([cx, cy - 1]);
          }
          
          componentSizes.set(currentLabel, componentSize);
          currentLabel++;
        }
      }
    }
    
    // Find largest component
    let largestLabel = 0;
    let largestSize = 0;
    for (const [label, size] of componentSizes) {
      if (size > largestSize) {
        largestSize = size;
        largestLabel = label;
      }
    }
    
    if (largestLabel === 0) {
      console.warn(`No definite foreground detected in image: ${imageUrl}`);
      return { x1: 0, y1: 0, x2: 0, y2: 0, confidence: 0 };
    }
    
    // Find bounding box of the definite foreground
    let minX = width;
    let minY = height;
    let maxX = 0;
    let maxY = 0;
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        if (labels[y * width + x] === largestLabel) {
          minX = Math.min(minX, x);
          minY = Math.min(minY, y);
          maxX = Math.max(maxX, x);
          maxY = Math.max(maxY, y);
        }
      }
    }
    
    // Add 5% margin to allow for edge refinement
    const marginX = Math.round((maxX - minX) * 0.05);
    const marginY = Math.round((maxY - minY) * 0.05);
    
    const x1 = Math.max(0, minX - marginX);
    const y1 = Math.max(0, minY - marginY);
    const x2 = Math.min(width, maxX + marginX);
    const y2 = Math.min(height, maxY + marginY);
    
    // Calculate confidence
    const chopAreaRatio = largestSize / (width * height);
    const boundingBoxArea = (x2 - x1) * (y2 - y1);
    const fillRatio = boundingBoxArea > 0 ? largestSize / boundingBoxArea : 0;
    
    let confidence = 0.5;
    if (chopAreaRatio > 0.15 && chopAreaRatio < 0.7) confidence += 0.2;
    if (fillRatio > 0.3) confidence += 0.3;
    
    console.log(`Detected chop: (${x1},${y1}) to (${x2},${y2}), confidence: ${confidence.toFixed(2)}`);
    
    return {
      x1,
      y1,
      x2,
      y2,
      confidence: Math.round(confidence * 100) / 100
    };
    
  } catch (error) {
    console.error('Error detecting chop boundaries:', error);
    throw error;
  }
}

/**
 * Process image: crop to chop region and remove background
 * Maintains original orientation
 */
export async function processChopImage(imageUrl: string, coords: CropCoordinates): Promise<Buffer> {
  const response = await fetch(imageUrl);
  const imageBuffer = Buffer.from(await response.arrayBuffer());
  
  const image = sharp(imageBuffer);
  const metadata = await image.metadata();
  const width = metadata.width!;
  const height = metadata.height!;
  
  // Get raw pixel data
  const { data } = await image.raw().ensureAlpha().toBuffer({ resolveWithObject: true });
  
  // Create mask for chop pixels (everything that's NOT blue background)
  const mask = new Uint8Array(width * height);
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const r = data[idx];
      const g = data[idx + 1];
      const b = data[idx + 2];
      
      // Same blue background detection as in detectChopBoundaries
      const isBlueBackground = 
        b > 85 &&
        b > r + 10 &&
        b > g + 10;
      
      // Keep everything that's NOT blue background
      if (!isBlueBackground) {
        mask[y * width + x] = 1;
      }
    }
  }
  
  // Apply morphological closing first to fill small blue holes inside the chop
  const closed = new Uint8Array(width * height);
  const closeKernel = 3;
  const closeRadius = Math.floor(closeKernel / 2);
  
  // Dilation
  const dilatedTemp = new Uint8Array(width * height);
  for (let y = closeRadius; y < height - closeRadius; y++) {
    for (let x = closeRadius; x < width - closeRadius; x++) {
      let hasAny = 0;
      for (let ky = -closeRadius; ky <= closeRadius; ky++) {
        for (let kx = -closeRadius; kx <= closeRadius; kx++) {
          if (mask[(y + ky) * width + (x + kx)] === 1) {
            hasAny = 1;
            break;
          }
        }
        if (hasAny) break;
      }
      dilatedTemp[y * width + x] = hasAny;
    }
  }
  
  // Erosion (to complete closing operation)
  for (let y = closeRadius; y < height - closeRadius; y++) {
    for (let x = closeRadius; x < width - closeRadius; x++) {
      let allPresent = 1;
      for (let ky = -closeRadius; ky <= closeRadius; ky++) {
        for (let kx = -closeRadius; kx <= closeRadius; kx++) {
          if (dilatedTemp[(y + ky) * width + (x + kx)] !== 1) {
            allPresent = 0;
            break;
          }
        }
        if (!allPresent) break;
      }
      closed[y * width + x] = allPresent;
    }
  }
  
  // Apply morphological opening - erosion then dilation to separate tag from chop
  const eroded = new Uint8Array(width * height);
  const kernelSize = 7;
  const kernelRadius = Math.floor(kernelSize / 2);
  
  for (let y = kernelRadius; y < height - kernelRadius; y++) {
    for (let x = kernelRadius; x < width - kernelRadius; x++) {
      let sum = 0;
      for (let ky = -kernelRadius; ky <= kernelRadius; ky++) {
        for (let kx = -kernelRadius; kx <= kernelRadius; kx++) {
          sum += closed[(y + ky) * width + (x + kx)];
        }
      }
      eroded[y * width + x] = sum > (kernelSize * kernelSize * 0.7) ? 1 : 0;
    }
  }
  
  const cleaned = eroded;
  
  // Find connected components and keep only the largest
  const labels = new Int32Array(width * height);
  let currentLabel = 1;
  const componentSizes = new Map<number, number>();
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (cleaned[y * width + x] === 1 && labels[y * width + x] === 0) {
        const stack = [[x, y]];
        let componentSize = 0;
        
        while (stack.length > 0) {
          const [cx, cy] = stack.pop()!;
          if (cx < 0 || cx >= width || cy < 0 || cy >= height) continue;
          if (labels[cy * width + cx] !== 0 || cleaned[cy * width + cx] !== 1) continue;
          
          labels[cy * width + cx] = currentLabel;
          componentSize++;
          
          stack.push([cx + 1, cy]);
          stack.push([cx - 1, cy]);
          stack.push([cx, cy + 1]);
          stack.push([cx, cy - 1]);
        }
        
        componentSizes.set(currentLabel, componentSize);
        currentLabel++;
      }
    }
  }
  
  // Find largest component
  let largestLabel = 0;
  let largestSize = 0;
  for (const [label, size] of componentSizes) {
    if (size > largestSize) {
      largestSize = size;
      largestLabel = label;
    }
  }
  
  // GrabCut-style iterative refinement: expand the mask and check each pixel
  // More aggressive expansion to capture all edge pixels
  const refined = new Uint8Array(width * height);
  const expandKernel = 25; // Very aggressive expansion
  const expandRadius = Math.floor(expandKernel / 2);
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (labels[y * width + x] === largestLabel) {
        // For each chop pixel, expand and mark neighbors as potential chop
        for (let dy = -expandRadius; dy <= expandRadius; dy++) {
          for (let dx = -expandRadius; dx <= expandRadius; dx++) {
            const ny = y + dy;
            const nx = x + dx;
            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
              const nidx = (ny * width + nx) * 4;
              const nr = data[nidx];
              const ng = data[nidx + 1];
              const nb = data[nidx + 2];
              
              // Only include if NOT clearly blue
              const isDefinitelyBlue = nb > 140 && nb > nr + 30 && nb > ng + 25;
              if (!isDefinitelyBlue) {
                refined[ny * width + nx] = 1;
              }
            }
          }
        }
      }
    }
  }
  
  // Create final mask output
  const finalMask = refined;
  
  // Create alpha channel - use final mask
  const outputData = Buffer.alloc(width * height * 4);
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const r = data[idx];
      const g = data[idx + 1];
      const b = data[idx + 2];
      
      // Show pixels that belong to the final chop mask
      if (finalMask[y * width + x] === 1) {
        outputData[idx] = r;
        outputData[idx + 1] = g;
        outputData[idx + 2] = b;
        outputData[idx + 3] = 255; // Opaque
      } else {
        // White background
        outputData[idx] = 255;
        outputData[idx + 1] = 255;
        outputData[idx + 2] = 255;
        outputData[idx + 3] = 255;
      }
    }
  }
  
  // Create image, crop to bounding box, maintain original orientation
  const processed = sharp(outputData, {
    raw: {
      width,
      height,
      channels: 4
    }
  })
  .extract({
    left: coords.x1,
    top: coords.y1,
    width: coords.x2 - coords.x1,
    height: coords.y2 - coords.y1
  });
  
  return processed.jpeg({ quality: 95 }).toBuffer();
}
