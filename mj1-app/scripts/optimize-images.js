#!/usr/bin/env node
import sharp from 'sharp';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function optimizeImage(inputPath, outputDir) {
  const filename = path.basename(inputPath, path.extname(inputPath));

  // Create multiple optimized versions
  const sizes = [
    { width: 80, suffix: '-80' },   // For logo in navbar
    { width: 120, suffix: '-120' }, // For loading screen
    { width: 180, suffix: '-180' }, // For retina displays
  ];

  console.log(`Optimizing ${inputPath}...`);

  // Ensure output directory exists
  await fs.mkdir(outputDir, { recursive: true });

  for (const size of sizes) {
    // WebP version (best compression)
    await sharp(inputPath)
      .resize(size.width, size.width, {
        fit: 'contain',
        background: { r: 255, g: 255, b: 255, alpha: 0 }
      })
      .webp({ quality: 85 })
      .toFile(path.join(outputDir, `${filename}${size.suffix}.webp`));

    // AVIF version (even better compression, newer format)
    await sharp(inputPath)
      .resize(size.width, size.width, {
        fit: 'contain',
        background: { r: 255, g: 255, b: 255, alpha: 0 }
      })
      .avif({ quality: 80 })
      .toFile(path.join(outputDir, `${filename}${size.suffix}.avif`));

    // Optimized PNG fallback
    await sharp(inputPath)
      .resize(size.width, size.width, {
        fit: 'contain',
        background: { r: 255, g: 255, b: 255, alpha: 0 }
      })
      .png({ compressionLevel: 9, adaptiveFiltering: true })
      .toFile(path.join(outputDir, `${filename}${size.suffix}.png`));
  }

  // Also create a favicon.ico
  await sharp(inputPath)
    .resize(32, 32)
    .toFile(path.join(outputDir, 'favicon.ico'));

  // Get file sizes for comparison
  const originalStats = await fs.stat(inputPath);
  const webpStats = await fs.stat(path.join(outputDir, `${filename}-80.webp`));

  console.log(`✅ Original: ${(originalStats.size / 1024 / 1024).toFixed(2)} MB`);
  console.log(`✅ Optimized WebP: ${(webpStats.size / 1024).toFixed(2)} KB`);
  console.log(`✅ Reduction: ${((1 - webpStats.size / originalStats.size) * 100).toFixed(1)}%`);
}

async function main() {
  const inputImage = path.join(__dirname, '..', 'public', 'mj1-fedora.png');
  const outputDir = path.join(__dirname, '..', 'public', 'images');

  try {
    await optimizeImage(inputImage, outputDir);
    console.log('\n🎉 Image optimization complete!');
    console.log('📁 Optimized images saved to:', outputDir);
  } catch (error) {
    console.error('Error optimizing images:', error);
    process.exit(1);
  }
}

main();