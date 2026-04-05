import { lookup } from "node:dns/promises";
import { validateOrigin } from "../utils/validateOrigin";

const BLOCKED_HOSTNAMES = new Set([
  "localhost",
  "127.0.0.1",
  "0.0.0.0",
  "[::1]",
]);

function isPrivateIP(ip: string): boolean {
  if (BLOCKED_HOSTNAMES.has(ip)) return true;
  if (ip.startsWith("10.")) return true;
  if (ip.startsWith("192.168.")) return true;
  if (ip.startsWith("169.254.")) return true;
  if (ip === "::1") return true;
  if (/^172\.(1[6-9]|2\d|3[01])\./.test(ip)) return true;
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

  if (BLOCKED_HOSTNAMES.has(parsed.hostname)) {
    return false;
  }

  if (
    parsed.hostname.endsWith(".internal") ||
    parsed.hostname.endsWith(".local")
  ) {
    return false;
  }

  try {
    const { address } = await lookup(parsed.hostname);
    if (isPrivateIP(address)) {
      return false;
    }
  } catch {
    return false;
  }

  try {
    const res = await fetch(url, {
      method: "HEAD",
      redirect: "manual",
      signal: AbortSignal.timeout(5000),
    });
    return res.ok;
  } catch {
    return false;
  }
});
