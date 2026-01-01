import { joinURL } from "ufo";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  const origin = getHeader(event, "origin");
  const referer = getHeader(event, "referer");
  const host = getHeader(event, "host");

  console.log("[PROXY] Request:", event.path, "| Origin:", origin, "| Host:", host);
  console.log("[PROXY] API_KEY:", config.apiKey ? "present" : "MISSING", "| API_BASE_URL:", config.apiBaseUrl);

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
    console.error("[PROXY] BLOCKED - Invalid origin:", origin, "| Allowed:", allowedOrigins);
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
    const result = await proxyRequest(event, url, { headers });
    console.log("[PROXY] SUCCESS:", path);
    return result;
  } catch (error) {
    console.error("[PROXY] ERROR:", path, error);
    throw error;
  }
});
