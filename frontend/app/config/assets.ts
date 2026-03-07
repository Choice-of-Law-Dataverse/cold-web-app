export const BLOB_STORAGE_BASE_URL =
  "https://choiceoflaw.blob.core.windows.net";

export const ASSET_BASE_URL = `${BLOB_STORAGE_BASE_URL}/assets`;

export const FLAG_BASE_URL = `${ASSET_BASE_URL}/flags/`;

export function flagUrl(alpha3Code: string): string {
  return `${FLAG_BASE_URL}${alpha3Code.toLowerCase()}.svg`;
}
