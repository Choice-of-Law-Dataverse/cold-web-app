import { joinURL } from "ufo";
import * as logfire from "@pydantic/logfire-node";
import { propagation, trace, context } from "@opentelemetry/api";
import { validateOrigin } from "../../utils/validateOrigin";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  validateOrigin(event, config);

  const path = event.path.replace(/^\/api\/proxy\//, "");
  const url = joinURL(config.apiBaseUrl, path);

  const headers: Record<string, string> = {
    "X-API-Key": config.apiKey,
  };

  // Propagate trace context to backend for distributed tracing
  const activeSpan = trace.getActiveSpan();
  if (activeSpan) {
    const ctx = trace.setSpan(context.active(), activeSpan);
    propagation.inject(ctx, headers);
  }

  const startTime = Date.now();

  try {
    const auth0Client = useAuth0(event);
    const accessTokenResult = await auth0Client.getAccessToken();

    if (accessTokenResult?.accessToken) {
      headers["Authorization"] = `Bearer ${accessTokenResult.accessToken}`;
    }
  } catch {
    /* noop */
  }

  try {
    const result = await proxyRequest(event, url, {
      headers,
    });

    return result;
  } catch (error) {
    const duration = Date.now() - startTime;
    logfire.error("Proxy request failed", {
      path,
      method: event.method,
      duration,
      error: error instanceof Error ? error.message : String(error),
    });
    throw error;
  }
});
