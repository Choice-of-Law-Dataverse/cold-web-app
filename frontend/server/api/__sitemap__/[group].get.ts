import * as logfire from "@pydantic/logfire-node";
import {
  SITEMAP_GROUPS,
  SITEMAP_MAX_PAGES,
  SITEMAP_PAGE_SIZE,
  toSitemapLocations,
  type EntityListResponse,
  type SitemapGroup,
} from "../../utils/sitemapSources";

async function fetchGroupLocations(
  group: SitemapGroup,
  apiBaseUrl: string,
  apiKey: string,
): Promise<string[]> {
  const locations: string[] = [];

  for (let page = 1; page <= SITEMAP_MAX_PAGES; page++) {
    const response = await $fetch<EntityListResponse>(
      `${apiBaseUrl}/entities/${group.slug}`,
      {
        headers: { "X-API-Key": apiKey },
        query: { page, page_size: SITEMAP_PAGE_SIZE },
      },
    );

    const items = response.items ?? [];
    locations.push(...toSitemapLocations(group, items));

    if (items.length < SITEMAP_PAGE_SIZE) break;
  }

  return locations;
}

export default defineSitemapEventHandler(async (event) => {
  const name = getRouterParam(event, "group") ?? "";
  const group = SITEMAP_GROUPS[name];

  if (!group) {
    throw createError({
      statusCode: 404,
      statusMessage: `Unknown sitemap group: ${name}`,
    });
  }

  const config = useRuntimeConfig();

  try {
    const locations = await fetchGroupLocations(
      group,
      String(config.apiBaseUrl ?? ""),
      String(config.apiKey ?? ""),
    );

    return locations.map((loc) => ({
      loc,
      priority: group.priority,
      changefreq: group.changefreq,
    }));
  } catch (error) {
    logfire.error("Sitemap source failed", {
      group: name,
      error: error instanceof Error ? error.message : String(error),
    });
    throw error;
  }
});
