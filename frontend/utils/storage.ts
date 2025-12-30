interface PdfAttachment {
  url: string;
  title: string;
  mimetype: string;
  size: number;
  icon: string;
  id: string;
}

/**
 * Storage proxy API endpoint prefix
 */
export const STORAGE_PROXY_PATH = "/api/storage";

/**
 * Extracts the storage path from a full URL
 * Example: https://domain.com/nc/uploads/noco/file.pdf -> nc/uploads/noco/file.pdf
 */
export function extractStoragePath(url: string): string | null {
  try {
    const urlObj = new URL(url);
    // Remove leading slash from pathname
    return urlObj.pathname.substring(1);
  } catch (error) {
    console.error("Failed to parse URL:", error, url);
    return null;
  }
}

/**
 * Constructs a proxy URL from a storage path
 * Example: nc/uploads/noco/file.pdf -> /api/storage/nc/uploads/noco/file.pdf
 */
export function buildProxyUrl(storagePath: string): string {
  return `${STORAGE_PROXY_PATH}/${storagePath}`;
}

/**
 * Extracts storage path from a proxy URL
 * Example: /api/storage/nc/uploads/noco/file.pdf -> nc/uploads/noco/file.pdf
 */
export function parseProxyUrl(proxyUrl: string): string {
  return proxyUrl.replace(new RegExp(`^${STORAGE_PROXY_PATH}/`), "");
}

/**
 * Utility function to convert PDF field from backend to internal proxy URL
 * The backend returns PDF data as a JSON array of objects or Python dict string
 * Example: [{"url":"https://...","title":"...","mimetype":"...","size":...,"icon":"...","id":"..."}]
 * Returns: /api/storage/nc/uploads/noco/...
 */
export function getPdfProxyUrl(pdfField: unknown): string | null {
  if (!pdfField) return null;

  console.log("getPdfProxyUrl input:", pdfField, typeof pdfField);

  let extractedUrl: string | null = null;

  // Handle when pdfField is already an object (not a string)
  if (typeof pdfField === "object" && pdfField !== null) {
    // Handle array format - take the first element
    if (Array.isArray(pdfField) && pdfField.length > 0) {
      extractedUrl = (pdfField[0] as PdfAttachment).url || null;
    }
    // Handle object format (backward compatibility)
    else if (!Array.isArray(pdfField) && "url" in pdfField) {
      extractedUrl = (pdfField as PdfAttachment).url || null;
    }
  }
  // Handle when pdfField is a string that needs parsing
  else if (typeof pdfField === "string") {
    try {
      // Try to fix Python dict format (single quotes) to JSON format (double quotes)
      let jsonString = pdfField;
      if (pdfField.includes("'")) {
        jsonString = pdfField.replace(/'/g, '"');
      }

      const pdfData = JSON.parse(jsonString) as PdfAttachment[] | PdfAttachment;

      // Handle array format - take the first element
      if (Array.isArray(pdfData) && pdfData.length > 0) {
        extractedUrl = pdfData[0].url || null;
      }
      // Handle object format (backward compatibility)
      else if (
        typeof pdfData === "object" &&
        pdfData !== null &&
        !Array.isArray(pdfData)
      ) {
        extractedUrl = pdfData.url || null;
      }
    } catch (e) {
      console.error("Failed to parse PDF field:", e);
      return null;
    }
  }

  if (extractedUrl) {
    const storagePath = extractStoragePath(extractedUrl);
    if (storagePath) {
      const proxyUrl = buildProxyUrl(storagePath);
      console.log("getPdfProxyUrl output:", proxyUrl);
      return proxyUrl;
    }
  }

  return null;
}
