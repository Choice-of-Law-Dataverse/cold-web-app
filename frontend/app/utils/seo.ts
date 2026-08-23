const DESCRIPTION_MAX_LENGTH = 160;
const SITE_SUFFIX = "CoLD";
const TITLE_SEPARATOR = " — ";

/**
 * Collapses markup, entities and runs of whitespace into a single-line string.
 *
 * Backend fields carry HTML fragments and hard-wrapped legal text; both render
 * badly inside a `<meta>` tag.
 */
export function stripMarkup(value: string | null | undefined): string {
  if (!value) return "";
  return value
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Keeps the first occurrence of each distinct part.
 *
 * Overlap matters as much as exact repetition: a case citation usually embeds
 * the case title, and joining both produces titles like
 * "Klausner v Berkovitz — Klausner v Berkovitz, CA 750/79, …".
 */
function cleanParts(parts: (string | null | undefined)[]): string[] {
  const result: string[] = [];
  const kept: string[] = [];

  for (const part of parts) {
    const cleaned = stripMarkup(part);
    if (!cleaned) continue;

    const key = cleaned.toLowerCase();
    const overlaps = kept.some(
      (existing) => existing.includes(key) || key.includes(existing),
    );
    if (overlaps) continue;

    kept.push(key);
    result.push(cleaned);
  }

  return result;
}

/**
 * Builds a `<title>`, always ending in the site name.
 *
 * @param parts Most specific first; blank and duplicate parts are dropped.
 * @param fallback Entity label used when no part carries information.
 */
export function buildPageTitle(
  parts: (string | null | undefined)[],
  fallback: string,
): string {
  const cleaned = cleanParts(parts);
  const segments = cleaned.length > 0 ? cleaned : [stripMarkup(fallback)];
  return [...segments, SITE_SUFFIX]
    .filter(Boolean)
    .join(TITLE_SEPARATOR)
    .slice(0, 120);
}

/**
 * Truncates on a word boundary and appends an ellipsis when text was dropped.
 */
export function truncate(
  value: string,
  maxLength: number = DESCRIPTION_MAX_LENGTH,
): string {
  if (value.length <= maxLength) return value;
  const clipped = value.slice(0, maxLength - 1);
  const lastSpace = clipped.lastIndexOf(" ");
  const base =
    lastSpace > maxLength * 0.6 ? clipped.slice(0, lastSpace) : clipped;
  return `${base.replace(/[\s,.;:—-]+$/, "")}…`;
}

/**
 * Builds a `<meta name="description">` from the most descriptive fields
 * available, falling back to a generic sentence when a record is sparse.
 *
 * Returning the title verbatim — as the previous implementation did — makes
 * every page look duplicated to a crawler, so callers should pass real content.
 */
export function buildSeoDescription(
  parts: (string | null | undefined)[],
  fallback: string,
  maxLength: number = DESCRIPTION_MAX_LENGTH,
): string {
  const cleaned = cleanParts(parts);
  const joined = cleaned.join(". ").replace(/\.\.+/g, ".");
  return truncate(joined || stripMarkup(fallback), maxLength);
}

/**
 * Normalises a route path into the form used for `rel=canonical`.
 *
 * Query strings and trailing slashes create duplicate URLs that all render the
 * same page, so they are stripped; the root path keeps its single slash.
 */
export function toCanonicalPath(path: string): string {
  const withoutQuery = path.split("?")[0]?.split("#")[0] ?? "/";
  if (withoutQuery === "" || withoutQuery === "/") return "/";
  const trimmed = withoutQuery.replace(/\/+$/, "");
  return trimmed === "" ? "/" : trimmed;
}

/** Joins a site origin and a path into an absolute URL without doubling slashes. */
export function toAbsoluteUrl(siteUrl: string, path: string): string {
  const origin = String(siteUrl || "").replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${origin}${suffix === "/" ? "/" : suffix}`;
}
