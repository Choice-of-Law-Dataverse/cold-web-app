import type { H3Event } from "h3";
import * as logfire from "@pydantic/logfire-node";

export function validateOrigin(
  event: H3Event,
  config: { public: { siteUrl: string } },
): void {
  const origin = getHeader(event, "origin");
  const referer = getHeader(event, "referer");

  if (!origin) {
    throw createError({
      statusCode: 403,
      message: "Forbidden: Missing origin",
    });
  }

  const allowedOrigins = [config.public.siteUrl].filter(Boolean);

  const isValidOrigin = allowedOrigins.some(
    (allowed) => origin === allowed || (referer && referer.startsWith(allowed)),
  );

  if (!isValidOrigin) {
    logfire.warning("Request blocked - invalid origin", {
      origin,
      referer,
      allowedOrigins,
    });
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid origin",
    });
  }
}
