export default defineEventHandler(async (event) => {
  const { url } = getQuery(event);

  if (!url || typeof url !== "string") {
    return false;
  }

  try {
    // If it's a local proxy URL, convert it to a full URL for checking
    let checkUrl = url;
    if (url.startsWith('/api/r2-proxy/')) {
      // For proxied R2 URLs, make a request to our own proxy endpoint
      const host = getHeader(event, 'host');
      const protocol = process.env.NODE_ENV === 'development' ? 'http' : 'https';
      checkUrl = `${protocol}://${host}${url}`;
    }
    
    const res = await fetch(checkUrl, { method: "HEAD" });
    return res.ok;
  } catch {
    return false;
  }
});
