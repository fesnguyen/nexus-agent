import imageCompression from 'browser-image-compression';

/**
 * Compresses an image file on the client side and converts it to WebP format.
 * @param file The original File object from the file input.
 * @returns A promise that resolves to the compressed File object.
 */
export const compressImage = async (file: File): Promise<File> => {
  const options = {
    maxSizeMB: 1,            // Target file size limit (1MB)
    maxWidthOrHeight: 256,  // Max dimension limit (scales down proportionally)
    useWebWorker: true,      // Processes in background thread to avoid UI freezing
    fileType: 'image/webp',  // Highly efficient modern image format
  };

  try {
    // 1. Perform the compression to a Blob
    const compressedBlob = await imageCompression(file, options);
    
    // 2. Extract filename without original extension
    const fileNameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
    
    // 3. Rebuild a clean File object
    return new File([compressedBlob], `${fileNameWithoutExt}.webp`, {
      type: 'image/webp',
    });
  } catch (error) {
    console.error('Error during image compression:', error);
    throw error;
  }
};