// Utility to check if cookies are allowed before initializing analytics or setting cookies
export function isCookieConsentAllowed() {
  if (typeof window === 'undefined') return false
  return localStorage.getItem('cookieConsent') === 'true'
}
