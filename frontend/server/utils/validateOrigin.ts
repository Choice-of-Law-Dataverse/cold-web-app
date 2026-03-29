import type { H3Event } from "h3";
import * as logfire from "@pydantic/logfire-node";

export function validateOrigin(
  event: H3Event,
  config: { public: { siteUrl: string } },
): void {
  const origin = getHeader(event, "origin");
  const referer = getHeader(event, "referer");
  const host = getHeader(event, "host");

  const allowedOrigins = [
    `https://${host}`,
    `http://${host}`,
    config.public.siteUrl,
  ].filter(Boolean);

  const sourceHeader = origin || referer;
  if (!sourceHeader) {
    logfire.warning("Request blocked - no origin or referer header", {
      host,
    });
    throw createError({
      statusCode: 403,
      message: "Forbidden: Missing origin",
    });
  }

  const isValidOrigin = allowedOrigins.some(
    (allowed) => origin === allowed || (referer && referer.startsWith(allowed)),
  );

  if (!isValidOrigin) {
    logfire.warning("Request blocked - invalid origin", {
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
}
