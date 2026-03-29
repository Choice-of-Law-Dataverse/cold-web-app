import type { LiteratureDetailResponse } from "@/types/entities/literature";

const BIBTEX_TYPE_MAP: Record<string, string> = {
  journalarticle: "article",
  book: "book",
  booksection: "incollection",
  thesis: "phdthesis",
  report: "techreport",
  preprint: "unpublished",
  presentation: "misc",
  encyclopediaarticle: "incollection",
  blogpost: "misc",
  document: "misc",
};

function toBibtexType(itemType?: string | null): string {
  if (!itemType) return "misc";
  return BIBTEX_TYPE_MAP[itemType.toLowerCase()] ?? "misc";
}

const JOURNAL_TYPES = new Set(["article"]);
const BOOKTITLE_TYPES = new Set(["incollection", "inproceedings"]);
const SCHOOL_TYPES = new Set(["phdthesis", "mastersthesis"]);
const RAW_FIELDS = new Set(["url", "doi"]);

function buildCitationKey(
  authors: string,
  title: string,
  year: string,
): string {
  if (authors && year) {
    const firstAuthorPart = authors.split(",")[0];
    const firstAuthor = firstAuthorPart?.trim().split(" ").pop();
    const cleanAuthor = firstAuthor?.replace(/[^a-zA-Z]/g, "").toLowerCase();
    return `${cleanAuthor ?? "unknown"}${year}`;
  }
  if (title && year) {
    const firstWordPart = title.split(" ")[0];
    const firstWord = (firstWordPart ?? "")
      .replace(/[^a-zA-Z]/g, "")
      .toLowerCase();
    return `${firstWord}${year}`;
  }
  return "cold_literature";
}

export function generateBibTeX(data: LiteratureDetailResponse): string {
  const entryType = toBibtexType(data.itemType);
  const itemTypeLower = data.itemType?.toLowerCase() ?? "";

  const s = (v?: string | null) => v ?? "";

  const escape = (str: string) =>
    str.replace(/[{}\\]/g, (char) => `\\${char}`).replace(/%/g, "\\%");

  const fields: string[] = [];
  const add = (key: string, value: string) => {
    if (value)
      fields.push(
        `  ${key} = {${RAW_FIELDS.has(key) ? value : escape(value)}}`,
      );
  };

  add("author", s(data.author));
  if (data.editor) add("editor", s(data.editor));
  add("title", s(data.title));

  if (JOURNAL_TYPES.has(entryType)) {
    add("journal", s(data.publicationTitle));
    add("journalabbrev", s(data.journalAbbreviation));
  } else if (BOOKTITLE_TYPES.has(entryType)) {
    add("booktitle", s(data.publicationTitle));
  }

  add("year", s(data.publicationYear));
  if (data.date) add("date", s(data.date));
  add("volume", s(data.volume));
  add("number", s(data.issue ?? data.number));
  add("pages", s(data.pages));
  add("edition", s(data.edition));

  if (data.series) {
    add("series", s(data.series));
    if (data.seriesNumber) add("seriesnumber", s(data.seriesNumber));
  }

  if (SCHOOL_TYPES.has(entryType)) {
    add("school", s(data.publisher));
    if (data.type) add("type", s(data.type));
  } else {
    add("publisher", s(data.publisher));
  }

  add("address", s(data.place));
  add("language", s(data.language));

  if (itemTypeLower === "blogpost")
    add("howpublished", data.url ? `\\url{${data.url}}` : "Blog");
  if (itemTypeLower === "presentation" && data.type) add("type", s(data.type));
  if (entryType === "unpublished") add("note", "Preprint");

  add("isbn", s(data.isbn));
  add("issn", s(data.issn));
  add("doi", s(data.doi));
  add("url", s(data.url));

  if (data.abstractNote) add("abstract", s(data.abstractNote));

  const citationKey = buildCitationKey(
    s(data.author),
    s(data.title),
    s(data.publicationYear),
  );
  return `@${entryType}{${citationKey},\n${fields.join(",\n")},\n}`;
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
