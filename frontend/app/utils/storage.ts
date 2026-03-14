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
function extractUrlFromPdfData(
  data: PdfAttachment[] | PdfAttachment,
): string | null {
  if (Array.isArray(data) && data.length > 0) {
    return data[0]?.url || null;
  }
  if (typeof data === "object" && data !== null && "url" in data) {
    return (data as PdfAttachment).url || null;
  }
  return null;
}

export function getPdfProxyUrl(pdfField: unknown): string | null {
  if (!pdfField) return null;

  let parsed: PdfAttachment[] | PdfAttachment;

  if (typeof pdfField === "object" && pdfField !== null) {
    parsed = pdfField as PdfAttachment[] | PdfAttachment;
  } else if (typeof pdfField === "string") {
    try {
      const jsonString = pdfField.includes("'")
        ? pdfField.replace(/'/g, '"')
        : pdfField;
      parsed = JSON.parse(jsonString) as PdfAttachment[] | PdfAttachment;
    } catch {
      return null;
    }
  } else {
    return null;
  }

  const extractedUrl = extractUrlFromPdfData(parsed);
  if (!extractedUrl) return null;

  const storagePath = extractStoragePath(extractedUrl);
  return storagePath ? buildProxyUrl(storagePath) : null;
}
