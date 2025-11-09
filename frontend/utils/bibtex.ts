/**
 * Generate BibTeX citation from literature record data
 */
export function generateBibTeX(data: Record<string, unknown>): string {
  const authors = (data.Authors || data.Author || "") as string;
  const title = (data.Title || "") as string;
  const year = (data.Year || data["Publication Year"] || "") as string;
  const journal = (data["Publication Title"] || data.Journal || "") as string;
  const volume = (data.Volume || "") as string;
  const pages = (data.Pages || "") as string;
  const publisher = (data.Publisher || "") as string;
  const doi = (data.DOI || "") as string;
  const url = (data.Url || data.URL || "") as string;

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
  if (volume) bibtex += `  volume = {${volume}},\n`;
  if (pages) bibtex += `  pages = {${pages}},\n`;
  if (publisher) bibtex += `  publisher = {${escape(publisher)}},\n`;
  if (doi) bibtex += `  doi = {${doi}},\n`;
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
