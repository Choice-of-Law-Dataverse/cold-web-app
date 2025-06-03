// This plugin blocks Google Analytics (gtag) until cookie consent is given
import { isCookieConsentAllowed } from '@/utils/cookieConsent.js'

export default defineNuxtPlugin((nuxtApp) => {
  // Only run on client
  if (process.server) return

  // Remove gtag script if consent not given
  if (!isCookieConsentAllowed()) {
    // Remove gtag script tags if present
    const gtagScript = document.querySelector(
      'script[src*="googletagmanager.com/gtag/js"]'
    )
    if (gtagScript) gtagScript.remove()
    // Remove any inline gtag init scripts
    document.querySelectorAll('script').forEach((script) => {
      if (script.innerText.includes('gtag(')) script.remove()
    })
    // Block gtag function
    window.dataLayer = window.dataLayer || []
    window.gtag = function () {
      /* blocked until consent */
    }
  }

  // Listen for consent change
  window.addEventListener('storage', (event) => {
    if (event.key === 'cookieConsent' && event.newValue === 'true') {
      // Reload to allow analytics
      window.location.reload()
    }
  })
})
