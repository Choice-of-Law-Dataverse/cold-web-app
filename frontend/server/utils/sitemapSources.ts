/** Largest `page_size` the backend accepts on `/entities/{slug}`. */
export const SITEMAP_PAGE_SIZE = 250;

/** Hard stop so a backend paging bug cannot spin this handler forever. */
export const SITEMAP_MAX_PAGES = 40;

export interface SitemapGroup {
  /** Backend `/entities/{slug}` collection. */
  slug: string;
  /** Route prefix the coldId is appended to. */
  path: string;
  priority: 0.5 | 0.6 | 0.7 | 0.8 | 0.9;
  changefreq: "daily" | "weekly" | "monthly" | "yearly";
}

/**
 * Entity collections published in the sitemap, keyed by the sitemap name used
 * in `nuxt.config.ts`.
 *
 * `questions` covers the 60 comparative question pages only. The ~15k
 * jurisdiction-specific answers under the same route (`/question/{JUR}_{id}`)
 * are `noindex` thin content and stay out, so crawl budget reaches the
 * jurisdiction reports that aggregate them instead.
 */
export const SITEMAP_GROUPS: Record<string, SitemapGroup> = {
  "court-decisions": {
    slug: "court-decisions",
    path: "/court-decision",
    priority: 0.8,
    changefreq: "monthly",
  },
  jurisdictions: {
    slug: "jurisdictions",
    path: "/jurisdiction",
    priority: 0.9,
    changefreq: "weekly",
  },
  literature: {
    slug: "literature",
    path: "/literature",
    priority: 0.6,
    changefreq: "monthly",
  },
  "domestic-instruments": {
    slug: "domestic-instruments",
    path: "/domestic-instrument",
    priority: 0.8,
    changefreq: "monthly",
  },
  "regional-instruments": {
    slug: "regional-instruments",
    path: "/regional-instrument",
    priority: 0.8,
    changefreq: "monthly",
  },
  "international-instruments": {
    slug: "international-instruments",
    path: "/international-instrument",
    priority: 0.8,
    changefreq: "monthly",
  },
  "arbitral-awards": {
    slug: "arbitral-awards",
    path: "/arbitral-award",
    priority: 0.6,
    changefreq: "monthly",
  },
  "arbitral-institutions": {
    slug: "arbitral-institutions",
    path: "/arbitral-institution",
    priority: 0.6,
    changefreq: "monthly",
  },
  "arbitral-rules": {
    slug: "arbitral-rules",
    path: "/arbitral-rule",
    priority: 0.6,
    changefreq: "monthly",
  },
  specialists: {
    slug: "specialists",
    path: "/specialist",
    priority: 0.5,
    changefreq: "monthly",
  },
  questions: {
    slug: "questions",
    path: "/question",
    priority: 0.7,
    changefreq: "monthly",
  },
};

export interface EntityListResponse {
  items?: { coldId?: string | null }[];
  total?: number;
}

/**
 * Turns a page of `/entities/{slug}` items into sitemap locations.
 *
 * Records without a `coldId` have no reachable detail route, so they are
 * skipped rather than emitted as a URL that would 404.
 */
export function toSitemapLocations(
  group: SitemapGroup,
  items: { coldId?: string | null }[],
): string[] {
  return items
    .map((item) => (item.coldId ?? "").trim())
    .filter((coldId) => coldId !== "")
    .map((coldId) => `${group.path}/${encodeURIComponent(coldId)}`);
}
