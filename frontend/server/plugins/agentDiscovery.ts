import { buildLinkHeader } from "../utils/agentDiscovery";

export default defineNitroPlugin((nitroApp) => {
  const config = useRuntimeConfig();
  const linkHeader = buildLinkHeader(config.apiBaseUrl);

  nitroApp.hooks.hook("render:response", (response) => {
    response.headers = {
      ...response.headers,
      link: response.headers?.link
        ? `${response.headers.link}, ${linkHeader}`
        : linkHeader,
    };
  });
});
