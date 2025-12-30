interface PdfAttachment {
  url: string;
  title: string;
  mimetype: string;
  size: number;
  icon: string;
  id: string;
}

/**
 * Utility function to extract PDF URL from backend PDF field
 * The backend returns PDF data as a JSON array of objects
 * Example: [{"url":"https://...","title":"...","mimetype":"...","size":...,"icon":"...","id":"..."}]
 */
export function extractPdfUrl(pdfField: unknown): string | null {
  if (!pdfField || typeof pdfField !== "string") return null;

  try {
    const pdfData = JSON.parse(pdfField) as PdfAttachment[] | PdfAttachment;

    // Handle array format - take the first element
    if (Array.isArray(pdfData) && pdfData.length > 0) {
      return pdfData[0].url || null;
    }

    // Handle object format (backward compatibility)
    if (
      typeof pdfData === "object" &&
      pdfData !== null &&
      !Array.isArray(pdfData)
    ) {
      return pdfData.url || null;
    }

    return null;
  } catch (e) {
    console.error("Failed to parse PDF field:", e);
    return null;
  }
}
