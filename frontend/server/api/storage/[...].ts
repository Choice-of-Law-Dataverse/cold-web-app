/**
 * Extracts storage path from a proxy URL
 * Example: /api/storage/nc/uploads/noco/file.pdf -> nc/uploads/noco/file.pdf
 */
function parseProxyUrl(proxyUrl: string): string {
  return proxyUrl.replace(/^\/api\/storage\//, "");
}

/**
 * Generate presigned URL using AWS Signature V4
 * This is a simplified implementation that works with Cloudflare R2
 */
async function generatePresignedUrl(
  accountId: string,
  bucketName: string,
  accessKeyId: string,
  secretAccessKey: string,
  key: string,
  expiresIn: number = 3600,
): Promise<string> {
  const crypto = await import("crypto");

  const region = "auto";
  const service = "s3";
  const endpoint = `https://${accountId}.r2.cloudflarestorage.com`;
  const host = `${accountId}.r2.cloudflarestorage.com`;

  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");
  const dateStamp = amzDate.substring(0, 8);

  // Encode the path properly for S3
  const encodedKey = key
    .split("/")
    .map((part) => encodeURIComponent(part))
    .join("/");
  const canonicalUri = `/${bucketName}/${encodedKey}`;
  const canonicalQueryString = `X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=${encodeURIComponent(`${accessKeyId}/${dateStamp}/${region}/${service}/aws4_request`)}&X-Amz-Date=${amzDate}&X-Amz-Expires=${expiresIn}&X-Amz-SignedHeaders=host`;

  const canonicalHeaders = `host:${host}\n`;
  const signedHeaders = "host";

  // For presigned URLs, use UNSIGNED-PAYLOAD
  const payloadHash = "UNSIGNED-PAYLOAD";

  const canonicalRequest = `GET\n${canonicalUri}\n${canonicalQueryString}\n${canonicalHeaders}\n${signedHeaders}\n${payloadHash}`;

  const algorithm = "AWS4-HMAC-SHA256";
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = `${algorithm}\n${amzDate}\n${credentialScope}\n${crypto.createHash("sha256").update(canonicalRequest).digest("hex")}`;

  const getSignatureKey = (
    key: string,
    dateStamp: string,
    regionName: string,
    serviceName: string,
  ) => {
    const kDate = crypto
      .createHmac("sha256", `AWS4${key}`)
      .update(dateStamp)
      .digest();
    const kRegion = crypto
      .createHmac("sha256", kDate)
      .update(regionName)
      .digest();
    const kService = crypto
      .createHmac("sha256", kRegion)
      .update(serviceName)
      .digest();
    const kSigning = crypto
      .createHmac("sha256", kService)
      .update("aws4_request")
      .digest();
    return kSigning;
  };

  const signingKey = getSignatureKey(
    secretAccessKey,
    dateStamp,
    region,
    service,
  );
  const signature = crypto
    .createHmac("sha256", signingKey)
    .update(stringToSign)
    .digest("hex");

  return `${endpoint}${canonicalUri}?${canonicalQueryString}&X-Amz-Signature=${signature}`;
}

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
      statusMessage: "Forbidden: Invalid origin",
    });
  }

  // Extract the R2 storage path from the request
  // Expected format: /api/storage/nc/uploads/noco/...
  const path = decodeURIComponent(parseProxyUrl(event.path));

  if (
    !config.r2AccessKeyId ||
    !config.r2SecretAccessKey ||
    !config.r2AccountId ||
    !config.r2BucketName
  ) {
    throw createError({
      statusCode: 500,
      statusMessage: "R2 credentials not configured",
    });
  }

  try {
    const presignedUrl = await generatePresignedUrl(
      config.r2AccountId,
      config.r2BucketName,
      config.r2AccessKeyId,
      config.r2SecretAccessKey,
      path,
      3600,
    );

    return sendRedirect(event, presignedUrl, 302);
  } catch (error) {
    console.error("Error generating presigned URL:", error);
    throw createError({
      statusCode: 500,
      statusMessage: "Failed to generate presigned URL",
    });
  }
});
