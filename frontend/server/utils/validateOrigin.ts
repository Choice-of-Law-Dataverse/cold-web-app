import type { H3Event } from "h3";
import * as logfire from "@pydantic/logfire-node";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

function withWwwVariant(url: URL): string {
  const alt = new URL(url.href);
  alt.hostname = url.hostname.startsWith("www.")
    ? url.hostname.slice(4)
    : `www.${url.hostname}`;
  return alt.origin;
}

export function buildAllowedOrigins(config: {
  public: Record<string, unknown>;
}): string[] {
  const origins: string[] = [];

  const siteUrl = String(config.public.siteUrl || "");
  if (siteUrl) {
    try {
      const parsed = new URL(siteUrl);
      origins.push(parsed.origin);
      origins.push(withWwwVariant(parsed));
    } catch {
      /* malformed siteUrl — skip */
    }
  }

  const extra = String(config.public.additionalOrigins || "");
  if (extra) {
    for (const raw of extra.split(",")) {
      try {
        const parsed = new URL(raw.trim());
        origins.push(parsed.origin);
        origins.push(withWwwVariant(parsed));
      } catch {
        /* malformed entry — skip */
      }
    }
  }

  const vercelHosts = [
    process.env.VERCEL_URL,
    process.env.VERCEL_BRANCH_URL,
    process.env.VERCEL_PROJECT_PRODUCTION_URL,
  ];
  for (const host of vercelHosts) {
    if (host) {
      origins.push(`https://${host}`);
    }
  }

  return origins;
}

export function validateOrigin(
  event: H3Event,
  config: { public: Record<string, unknown> },
): void {
  if (SAFE_METHODS.has(event.method)) {
    return;
  }

  const origin = getHeader(event, "origin");

  if (!origin) {
    throw createError({
      statusCode: 403,
      message: "Forbidden: Missing origin",
    });
  }

  let sourceOrigin: string;
  try {
    sourceOrigin = new URL(origin).origin;
  } catch {
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid origin",
    });
  }

  const allowedOrigins = buildAllowedOrigins(config);

  if (!allowedOrigins.includes(sourceOrigin)) {
    logfire.warning("Request blocked - invalid origin", {
      origin,
      allowedOrigins,
    });
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid origin",
    });
  }
}
