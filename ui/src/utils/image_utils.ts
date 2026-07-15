import imageCompression from "browser-image-compression";

/**
 * Resize an image before uploading to the backend.
 */
export const compressImage = async (
  file: File,
): Promise<File> => {
  const options = {
    // Resize only when necessary.
    maxWidthOrHeight: 1344,

    // Keep original image type.
    fileType: file.type,

    // High quality.
    initialQuality: 0.95,

    // Avoid unnecessary compression.
    maxSizeMB: 5,

    // Run in a worker.
    useWebWorker: true,

    // Preserve metadata if available.
    preserveExif: true,
  };

  try {
    const compressedFile = await imageCompression(
      file,
      options,
    );

    return new File(
      [compressedFile],
      file.name,
      {
        type: compressedFile.type,
        lastModified: Date.now(),
      },
    );
  } catch (error) {
    console.error(
      "Failed to preprocess image:",
      error,
    );

    throw error;
  }
};