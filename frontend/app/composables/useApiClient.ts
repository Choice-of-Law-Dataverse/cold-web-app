import createClient from "openapi-fetch";
import type { paths } from "@/types/api-schema";

/**
 * Typed client for the CoLD backend.
 *
 * In the browser every call goes through `/api/proxy` so the API key stays on
 * the server and the Auth0 session is attached. During SSR we talk to the
 * backend directly instead: routing a server render back out through our own
 * public origin would add a full network round-trip (plus a CDN hop) to every
 * request, which server-side prefetching makes hot path.
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
