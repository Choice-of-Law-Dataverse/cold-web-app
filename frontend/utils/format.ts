export function formatDate(dateString: string | null): string | null {
  if (!dateString) return null

  const date = new Date(dateString)

  // Check if it's January 1st
  const isFirstOfJanuary =
    date.getDate() === 1 && date.getMonth() === 0 // 0 = January

  if (isFirstOfJanuary) {
    return date.getFullYear().toString()
  }

  // Otherwise, return full formatted date
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date)
}
