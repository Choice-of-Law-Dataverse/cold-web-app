import { joinURL } from "ufo";

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

  return proxyRequest(event, url, { headers });
});
