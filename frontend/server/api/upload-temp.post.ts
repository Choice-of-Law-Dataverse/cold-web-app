import { BlobServiceClient } from "@azure/storage-blob";
import { DefaultAzureCredential } from "@azure/identity";
import { randomUUID } from "crypto";
import * as logfire from "@pydantic/logfire-node";

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();

  // Verify origin
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
    logfire.warning("Upload request blocked - invalid origin", {
      origin,
      referer,
      host,
    });
    throw createError({
      statusCode: 403,
      message: "Forbidden: Invalid origin",
    });
  }

  try {
    const body = await readBody<{
      file_name: string;
      file_content_base64: string;
    }>(event);

    if (!body?.file_name || !body?.file_content_base64) {
      throw createError({
        statusCode: 400,
        message: "Missing file_name or file_content_base64",
      });
    }

    // Decode base64 to buffer
    const fileBuffer = Buffer.from(body.file_content_base64, "base64");

    // Generate unique blob name
    const fileExtension = body.file_name.split(".").pop() || "pdf";
    const blobName = `temp/${randomUUID()}.${fileExtension}`;

    // Upload to Azure Blob Storage
    const accountName = config.azureStorageAccountName;
    const containerName = config.azureTempContainerName || "temp-uploads";
    const connectionString = config.azureStorageConnectionString;

    let blobServiceClient: BlobServiceClient;

    if (connectionString) {
      // Use connection string for local development
      blobServiceClient =
        BlobServiceClient.fromConnectionString(connectionString);
    } else if (accountName) {
      // Use managed identity for production
      const accountUrl = `https://${accountName}.blob.core.windows.net`;
      const credential = new DefaultAzureCredential();
      blobServiceClient = new BlobServiceClient(accountUrl, credential);
    } else {
      throw createError({
        statusCode: 500,
        message: "Azure Storage not configured",
      });
    }

    const containerClient = blobServiceClient.getContainerClient(containerName);
    const blockBlobClient = containerClient.getBlockBlobClient(blobName);

    // Upload with metadata
    await blockBlobClient.upload(fileBuffer, fileBuffer.length, {
      metadata: {
        original_filename: body.file_name,
        uploaded_at: new Date().toISOString(),
      },
    });

    const blobUrl = blockBlobClient.url;

    logfire.info("File uploaded to Azure Blob Storage", {
      blobName,
      blobUrl,
      originalFileName: body.file_name,
      size: fileBuffer.length,
    });

    return {
      blob_url: blobUrl,
      blob_name: blobName,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : undefined;

    logfire.error("Failed to upload file to Azure", {
      error: errorMessage,
      stack: errorStack,
    });

    console.error("Upload error:", errorMessage);
    console.error("Stack:", errorStack);

    throw createError({
      statusCode: 500,
      message: `Failed to upload file: ${errorMessage}`,
    });
  }
});
