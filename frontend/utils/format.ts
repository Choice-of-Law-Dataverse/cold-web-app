export function formatDate(dateString: string | null): string | null {
    if (!dateString) return null
  
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(date)
  }
  