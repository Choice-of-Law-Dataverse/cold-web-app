export const BLOB_STORAGE_BASE_URL = "https://assets.cold.global";

export const ASSET_BASE_URL = `${BLOB_STORAGE_BASE_URL}/assets`;

export const FLAG_BASE_URL = `${ASSET_BASE_URL}/flags/`;

export function flagUrl(coldId: string): string {
  return `${FLAG_BASE_URL}${coldId.toLowerCase()}.svg`;
}
