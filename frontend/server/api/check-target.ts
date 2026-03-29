import { validateOrigin } from "../utils/validateOrigin";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  validateOrigin(event, config);

  const { url } = getQuery(event);

  if (!url || typeof url !== "string") {
    return false;
  }

  try {
    const parsed = new URL(url);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      return false;
    }

    const hostname = parsed.hostname;
    if (
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      hostname === "::1" ||
      hostname === "0.0.0.0" ||
      hostname.startsWith("10.") ||
      hostname.startsWith("172.") ||
      hostname.startsWith("192.168.") ||
      hostname === "169.254.169.254" ||
      hostname.startsWith("169.254.") ||
      hostname.endsWith(".internal") ||
      hostname.endsWith(".local")
    ) {
      return false;
    }

    const res = await fetch(url, {
      method: "HEAD",
      redirect: "manual",
    });
    return res.ok;
  } catch {
    return false;
  }
});
