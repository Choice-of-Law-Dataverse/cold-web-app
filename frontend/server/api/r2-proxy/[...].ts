export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  const origin = getHeader(event, "origin");
  const referer = getHeader(event, "referer");
  const host = getHeader(event, "host");

  const allowedOrigins = [
    `http://localhost:3000`,
    `https://${host}`,
    `http://${host}`,
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
      statusMessage: "Forbidden: Invalid origin",
    });
  }

  // Extract the R2 storage path from the request
  // Expected format: /api/r2-proxy/nc/uploads/noco/...
  const path = event.path.replace(/^\/api\/r2-proxy\//, "");

  // Construct the full R2 URL using configured base URL
  const url = `${config.r2BaseUrl}/${path}`;

  // Proxy the request with authentication
  // R2 storage accessed through NocoDB might require the NocoDB API token
  return proxyRequest(event, url, {
    headers: {
      Authorization: `Bearer ${config.fastApiToken}`,
    },
  });
});
