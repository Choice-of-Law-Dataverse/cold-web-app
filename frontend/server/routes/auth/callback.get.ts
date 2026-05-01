import { defineEventHandler, sendRedirect } from "h3";
import * as logfire from "@pydantic/logfire-node";

export default defineEventHandler(async (event) => {
  const auth0Client = useAuth0(event);
  const auth0ClientOptions = event.context.auth0ClientOptions;

  try {
    const { appState } = await auth0Client.completeInteractiveLogin<
      { returnTo?: string } | undefined
    >(new URL(event.node.req.url as string, auth0ClientOptions.appBaseUrl));

    const target = toSameOriginRedirect(
      appState?.returnTo,
      auth0ClientOptions.appBaseUrl,
    );
    return sendRedirect(event, target);
  } catch (error) {
    logfire.warning("Auth0 callback failed; restarting login", {
      error: error instanceof Error ? error.message : String(error),
    });
    return sendRedirect(event, "/auth/login");
  }
});

function toSameOriginRedirect(
  candidate: string | undefined,
  baseUrl: string,
): string {
  if (!candidate) return baseUrl;
  try {
    const target = new URL(candidate, baseUrl);
    const base = new URL(baseUrl);
    return target.origin === base.origin ? target.toString() : baseUrl;
  } catch {
    return baseUrl;
  }
}
