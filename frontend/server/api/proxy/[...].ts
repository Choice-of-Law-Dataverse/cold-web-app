import { joinURL } from "ufo";
import * as logfire from "@pydantic/logfire-node";
import { propagation, trace, context } from "@opentelemetry/api";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  const origin = getHeader(event, "origin");
  const referer = getHeader(event, "referer");
  const host = getHeader(event, "host");

  const allowedOrigins = [
    `http://localhost:3000`,
    `https://${host}`,
    `http://${host}`,
    config.public.siteUrl,
  ];

  const isValidOrigin =
    !origin ||
    allowedOrigins.some(
      (allowed) =>
        origin === allowed || (referer && referer.startsWith(allowed)),
    );

  if (!isValidOrigin) {
    logfire.warning("Proxy request blocked - invalid origin", {
      origin,
      referer,
      host,
      allowedOrigins,
    });
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid origin",
    });
  }

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
