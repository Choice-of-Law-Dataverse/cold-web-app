import type { LiteratureResponse } from "@/types/entities/literature";

/**
 * Generate BibTeX citation from literature record data
 */
export function generateBibTeX(data: LiteratureResponse): string {
  const authors = data.Author || "";
  const title = data.Title || "";
  const year = data["Publication Year"] || "";
  const journal = data["Publication Title"] || "";
  const publisher = data.Publisher || "";
  const url = data.Url || "";

  // Generate citation key from first author's last name and year
  let citationKey = "cold_literature";
  if (authors && year) {
    const firstAuthor = authors.split(",")[0].trim().split(" ").pop();
    // Clean the author name for use in citation key
    const cleanAuthor = firstAuthor?.replace(/[^a-zA-Z]/g, "").toLowerCase();
    citationKey = `${cleanAuthor}${year}`;
  } else if (title && year) {
    // Fallback to first word of title + year
    const firstWord = title
      .split(" ")[0]
      .replace(/[^a-zA-Z]/g, "")
      .toLowerCase();
    citationKey = `${firstWord}${year}`;
  }

  // Escape special BibTeX characters in strings
  const escape = (str: string) =>
    str.replace(/[{}\\]/g, (char) => `\\${char}`).replace(/%/g, "\\%");

  let bibtex = `@article{${citationKey},\n`;
  if (authors) bibtex += `  author = {${escape(authors)}},\n`;
  if (title) bibtex += `  title = {${escape(title)}},\n`;
  if (journal) bibtex += `  journal = {${escape(journal)}},\n`;
  if (year) bibtex += `  year = {${year}},\n`;
  if (publisher) bibtex += `  publisher = {${escape(publisher)}},\n`;
  if (url) bibtex += `  url = {${url}},\n`;
  bibtex += "}";

  return bibtex;
}

/**
 * Sanitize filename for safe file download
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, "") // Remove invalid characters
    .replace(/\s+/g, "_") // Replace spaces with underscores
    .substring(0, 200); // Limit length
}

/**
 * Download text content as a file
 */
export function downloadFile(
  content: string,
  filename: string,
  mimeType: string,
): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
