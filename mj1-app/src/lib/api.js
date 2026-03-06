// API Configuration - Use relative URL in production
const API_URL = import.meta.env.VITE_API_URL || '';
const API_KEY = import.meta.env.VITE_API_KEY || '';
const MAX_IMAGE_SIZE_MB = parseInt(import.meta.env.VITE_MAX_IMAGE_SIZE_MB || '10');

export function validateImage(file) {
  if (!file) return { valid: false, error: 'No file provided' };

  if (!file.type.startsWith('image/')) {
    return { valid: false, error: 'File must be an image' };
  }

  const maxSizeBytes = MAX_IMAGE_SIZE_MB * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    return { valid: false, error: `Image must be less than ${MAX_IMAGE_SIZE_MB}MB` };
  }

  const allowedExtensions = ['jpg', 'jpeg', 'png'];
  const extension = file.name.split('.').pop().toLowerCase();
  if (!allowedExtensions.includes(extension)) {
    return { valid: false, error: 'Only JPG/JPEG and PNG images are supported' };
  }

  return { valid: true };
}

export function sanitizePrompt(prompt) {
  return prompt
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<[^>]+>/g, '')
    .slice(0, 1000);
}

export async function judgeImages(imageA, imageB, prompt, temperature = 0.0, maxTokens = 2048) {
  console.log('judgeImages called with:', {
    imageA: imageA ? `${typeof imageA} (length: ${imageA.length || 'N/A'})` : 'null',
    imageB: imageB ? `${typeof imageB} (length: ${imageB.length || 'N/A'})` : 'null',
    prompt
  });

  if (!imageA || !imageB || !prompt) {
    throw new Error('Missing required inputs');
  }

  try {
    const formData = new FormData();

    // Handle imageA - convert data URL to blob
    let blobA;
    console.log('Processing imageA:', typeof imageA, imageA?.slice?.(0, 50));
    if (typeof imageA === 'string' && imageA.startsWith('data:')) {
      console.log('ImageA is a data URL, fetching...');
      const responseA = await fetch(imageA);
      blobA = await responseA.blob();
      console.log('ImageA blob created:', blobA.size, blobA.type);
    } else if (imageA instanceof Blob || imageA instanceof File) {
      blobA = imageA;
    } else {
      const responseA = await fetch(imageA);
      blobA = await responseA.blob();
    }
    const validationA = validateImage(new File([blobA], 'imageA.jpg', { type: blobA.type }));
    if (!validationA.valid) throw new Error(validationA.error);
    formData.append('imageA', blobA, 'imageA.jpg');

    // Handle imageB - convert data URL to blob
    let blobB;
    if (imageB.startsWith('data:')) {
      const responseB = await fetch(imageB);
      blobB = await responseB.blob();
    } else if (imageB instanceof Blob || imageB instanceof File) {
      blobB = imageB;
    } else {
      const responseB = await fetch(imageB);
      blobB = await responseB.blob();
    }
    const validationB = validateImage(new File([blobB], 'imageB.jpg', { type: blobB.type }));
    if (!validationB.valid) throw new Error(validationB.error);
    formData.append('imageB', blobB, 'imageB.jpg');

    formData.append('prompt', sanitizePrompt(prompt));
    formData.append('temperature', temperature.toString());
    formData.append('maxTokens', maxTokens.toString());

    const headers = {};
    if (API_KEY) {
      headers['Authorization'] = `Bearer ${API_KEY}`;
    }

    const response = await fetch(`${API_URL}/api/judge`, {
      method: 'POST',
      headers,
      body: formData
    });

    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please try again in a minute.');
    }

    if (response.status === 403) {
      throw new Error('Authentication required. Running in demo mode.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }

    const result = await response.json();

    if (!result.winner || typeof result.scoreA !== 'number' || typeof result.scoreB !== 'number') {
      throw new Error('Invalid response from server');
    }

    return result;
  } catch (error) {
    console.error('API Error Full Details:', {
      message: error.message,
      stack: error.stack,
      name: error.name,
      error
    });

    if (error.message && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your connection.');
    }

    throw error;
  }
}