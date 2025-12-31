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

  let authToken = config.fastApiToken; // Default to the backend token

  const auth0Client = useAuth0(event);

  try {
    // Try to get the user's Auth0 token from the session
    const accessTokenResult = await auth0Client.getAccessToken();

    if (accessTokenResult) {
      // Use the user's Auth0 token if they're logged in
      authToken = accessTokenResult.accessToken;
    }
  } catch {
    // If there's any error getting the session, continue with the default token
    console.log("No user session found, using default token");
  }

  return proxyRequest(event, url, {
    headers: {
      Authorization: `Bearer ${authToken}`,
    },
  });
});
