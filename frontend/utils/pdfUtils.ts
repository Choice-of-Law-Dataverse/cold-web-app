/**
 * Utility function to extract PDF URL from backend PDF field
 * The backend returns PDF data as a string representation of a Python dict
 * 
 * Note: This uses simple string replacement to convert Python dict syntax to JSON.
 * This approach is fragile and may not work with escaped quotes or complex strings.
 * Ideally, the backend should return proper JSON format, but this works for the
 * current data format.
 */
export function extractPdfUrl(pdfField: unknown): string | null {
  if (!pdfField || typeof pdfField !== "string") return null;

  try {
    // The PDF field is a string representation of a Python dict
    // Example: "{'id': '...', 'url': '...', 'filename': '...', ...}"
    // We need to parse it carefully
    const jsonStr = pdfField.replace(/'/g, '"'); // Replace single quotes with double quotes
    const pdfData = JSON.parse(jsonStr);
    return pdfData.url || null;
  } catch (e) {
    // If parsing fails, return null
    console.error("Failed to parse PDF field:", e);
    return null;
  }
}
