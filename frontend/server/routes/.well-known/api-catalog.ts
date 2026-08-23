import { buildApiCatalog } from "../../utils/agentDiscovery";

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event);

  setResponseHeaders(event, {
    "content-type": "application/linkset+json",
    "cache-control": "public, max-age=3600",
  });

  return buildApiCatalog(config.apiBaseUrl);
});
