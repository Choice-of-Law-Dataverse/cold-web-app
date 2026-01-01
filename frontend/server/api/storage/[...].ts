import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import * as logfire from "@pydantic/logfire-node";

/**
 * Extracts storage path from a proxy URL
 * Example: /api/storage/nc/uploads/noco/file.pdf -> nc/uploads/noco/file.pdf
 */
function parseProxyUrl(proxyUrl: string): string {
  return proxyUrl.replace(/^\/api\/storage\//, "");
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
    config.public.siteUrl,
  ];

  const isValidOrigin =
    !origin ||
    allowedOrigins.some(
      (allowed) =>
        origin === allowed || (referer && referer.startsWith(allowed)),
    );

  if (!isValidOrigin) {
    logfire.warning("Storage request blocked - invalid origin", {
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

  // Extract the R2 storage path from the request
  // Expected format: /api/storage/nc/uploads/noco/...
  const path = decodeURIComponent(parseProxyUrl(event.path));

  if (
    !config.r2.accessKeyId ||
    !config.r2.secretAccessKey ||
    !config.r2.accountId ||
    !config.r2.bucketName
  ) {
    logfire.error("R2 credentials not configured", {
      hasAccessKeyId: !!config.r2.accessKeyId,
      hasSecretAccessKey: !!config.r2.secretAccessKey,
      hasAccountId: !!config.r2.accountId,
      hasBucketName: !!config.r2.bucketName,
    });
    throw createError({
      statusCode: 500,
      message: "R2 credentials not configured",
    });
  }

  try {
    const s3Client = new S3Client({
      region: "auto",
      endpoint: `https://${config.r2.accountId}.r2.cloudflarestorage.com`,
      credentials: {
        accessKeyId: config.r2.accessKeyId,
        secretAccessKey: config.r2.secretAccessKey,
      },
    });

    const command = new GetObjectCommand({
      Bucket: config.r2.bucketName,
      Key: path,
    });

    const presignedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: 3600,
    });

    return sendRedirect(event, presignedUrl, 302);
  } catch (error) {
    logfire.error("Failed to generate presigned URL", {
      path,
      bucket: config.r2.bucketName,
      error: error instanceof Error ? error.message : String(error),
    });
    throw createError({
      statusCode: 500,
      message: "Failed to generate presigned URL",
    });
  }
});
