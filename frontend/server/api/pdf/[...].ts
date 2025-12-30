import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

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
  // Expected format: /api/pdf/nc/uploads/noco/...
  const path = event.path.replace(/^\/api\/pdf\//, "");

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
    const s3Client = new S3Client({
      region: "auto",
      endpoint: `https://${config.r2AccountId}.r2.cloudflarestorage.com`,
      credentials: {
        accessKeyId: config.r2AccessKeyId,
        secretAccessKey: config.r2SecretAccessKey,
      },
    });

    const command = new GetObjectCommand({
      Bucket: config.r2BucketName,
      Key: path,
    });

    const presignedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: 3600,
    });

    return sendRedirect(event, presignedUrl, 302);
  } catch (error) {
    console.error("Error generating presigned URL:", error);
    throw createError({
      statusCode: 500,
      statusMessage: "Failed to generate presigned URL",
    });
  }
});
