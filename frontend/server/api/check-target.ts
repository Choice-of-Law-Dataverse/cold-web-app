import { validateOrigin } from "../utils/validateOrigin";

const BLOCKED_HOSTNAMES = new Set([
  "localhost",
  "127.0.0.1",
  "0.0.0.0",
  "[::1]",
  "metadata.google.internal",
]);

function isPrivateIP(hostname: string): boolean {
  if (BLOCKED_HOSTNAMES.has(hostname)) return true;
  if (hostname.startsWith("10.")) return true;
  if (hostname.startsWith("192.168.")) return true;
  if (hostname.startsWith("169.254.")) return true;
  if (/^172\.(1[6-9]|2\d|3[01])\./.test(hostname)) return true;
  return false;
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  validateOrigin(event, config);

  const { url } = getQuery(event);

  if (!url || typeof url !== "string") {
    return false;
  }

  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return false;
  }

  if (parsed.protocol !== "https:" && parsed.protocol !== "http:") {
    return false;
  }

  if (isPrivateIP(parsed.hostname)) {
    return false;
  }

  if (
    parsed.hostname.endsWith(".internal") ||
    parsed.hostname.endsWith(".local")
  ) {
    return false;
  }

  try {
    const res = await fetch(url, {
      method: "HEAD",
      redirect: "manual",
    });
    return res.ok;
  } catch {
    return false;
  }
});
