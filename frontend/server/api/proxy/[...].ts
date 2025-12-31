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

  // Try to get the user's Auth0 token from the session
  let authToken = config.fastApiToken; // Default to the backend token

  try {
    // Check if user is authenticated with Auth0
    const session = await getSession(event);
    if (session?.user?.accessToken) {
      // Use the user's Auth0 token if they're logged in
      authToken = session.user.accessToken;
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
