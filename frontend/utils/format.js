export function formatDate(dateString) {
  if (!dateString) return null;

  const date = new Date(dateString);

  const isFirstOfJanuary = date.getDate() === 1 && date.getMonth() === 0;

  if (isFirstOfJanuary) {
    return date.getFullYear().toString();
  }

  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function extractYear(dateString) {
  if (!dateString) return null;

  const date = new Date(dateString);
  return date.getFullYear().toString();
}
export function formatYear(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return isNaN(date) ? "" : date.getFullYear();
}
