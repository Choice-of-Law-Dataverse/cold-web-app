// plugins/manual-gtag.client.js
import { loadGtag } from '@/utils/gtag.js'

export default defineNuxtPlugin(() => {
  if (process.server) return
  if (localStorage.getItem('cookieConsent') === 'true') {
    loadGtag('G-ZSYHMWVVRH') // Alpha
    // loadGtag('G-C61ZX1L3NH') // Beta and live
  }
  // Listen for consent change and load gtag if user allows
  window.addEventListener('storage', (event) => {
    if (event.key === 'cookieConsent' && event.newValue === 'true') {
      loadGtag('G-ZSYHMWVVRH') // Alpha
      // loadGtag('G-C61ZX1L3NH') // Beta and Live
    }
  })
})
