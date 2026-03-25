import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import * as logfire from "@pydantic/logfire-node";
import { validateOrigin } from "../../utils/validateOrigin";

function parseProxyUrl(proxyUrl: string): string {
  return proxyUrl.replace(/^\/api\/storage\//, "");
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  validateOrigin(event, config);

  const path = decodeURIComponent(parseProxyUrl(event.path));

  if (!path.startsWith("nc/uploads/")) {
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid storage path",
    });
  }

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

    const PRESIGNED_URL_TTL_SECONDS = 3_600;
    const presignedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: PRESIGNED_URL_TTL_SECONDS,
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
