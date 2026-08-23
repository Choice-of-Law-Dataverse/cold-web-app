import { buildAiCatalog } from "../../utils/aiCatalog";

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event);

  setResponseHeaders(event, {
    "content-type": "application/json",
    "access-control-allow-origin": "*",
    "cache-control":
      "public, max-age=0, s-maxage=3600, stale-while-revalidate=86400",
  });

  return buildAiCatalog(String(config.public.siteUrl ?? ""), config.apiBaseUrl);
});
