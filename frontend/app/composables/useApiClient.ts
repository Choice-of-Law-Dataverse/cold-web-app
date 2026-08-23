import createClient from "openapi-fetch";
import type { paths } from "@/types/api-schema";

/**
 * Typed client for the CoLD backend.
 *
 * In the browser every call goes through `/api/proxy`, which attaches the API
 * key and the caller's Auth0 token server-side.
 *
 * During SSR we call the backend directly and attach the key ourselves,
 * because the proxy is only reachable over our own public origin: a render
 * would have to leave Azure, cross the CDN and re-enter this same process,
 * holding a second concurrent request slot while the first blocks on it.
 * Under crawl load that halves capacity and can deadlock a replica once it
 * hits max concurrency.
 *
 * Two things are traded away. The backend call no longer joins the
 * distributed trace, which is a real if minor loss. It also no longer carries
 * the user's token — deliberate, since server-rendered HTML has to stay
 * identical for every visitor to be safe for a shared cache.
 */
export function useApiClient() {
  const config = useRuntimeConfig();
  const isServer = typeof window === "undefined";
  const apiBaseUrl = String(config.apiBaseUrl ?? "");
  const callBackendDirectly = isServer && apiBaseUrl !== "";

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (callBackendDirectly) {
    headers["X-API-Key"] = String(config.apiKey ?? "");
  }

  const baseUrl = callBackendDirectly
    ? apiBaseUrl
    : isServer
      ? `${config.public.siteUrl}/api/proxy`
      : "/api/proxy";

  const client = createClient<paths>({ baseUrl, headers });

  return { client };
}
