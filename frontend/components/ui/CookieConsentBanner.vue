<template>
  <div v-if="showBanner" class="cookie-banner">
    <span class="prose">
      CoLD is cookie-free by default. Allowing them helps us improve the
      website.
    </span>
    <UButton
      class="link-button"
      variant="link"
      icon="i-material-symbols:cookie-outline"
      @click="acceptCookies"
    >
      <span>Allow cookies</span>
    </UButton>

    <UButton
      class="link-button"
      variant="link"
      icon="i-material-symbols:cookie-off-outline"
      @click="declineCookies"
    >
      <span>Continue cookie-free</span>
    </UButton>

    <UButton
      class="link-button"
      to="/disclaimer"
      variant="link"
      icon="i-material-symbols:arrow-forward"
      trailing
    >
      <span>Learn more</span>
    </UButton>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const showBanner = ref(false)

onMounted(() => {
  if (typeof window !== 'undefined') {
    // Ensure cookieConsent always exists on page load
    if (localStorage.getItem('cookieConsent') === null) {
      localStorage.setItem('cookieConsent', 'false')
    }
    const consent = localStorage.getItem('cookieConsent')
    const consentDate = localStorage.getItem('cookieConsentDate')
    const consentSet = localStorage.getItem('cookieConsentSet')
    let expired = false
    if (consentDate) {
      const now = new Date()
      const setDate = new Date(consentDate)
      // 1 year = 365 days
      const diffDays = (now - setDate) / (1000 * 60 * 60 * 24)
      if (diffDays >= 365) {
        expired = true
        localStorage.removeItem('cookieConsent')
        localStorage.removeItem('cookieConsentDate')
        localStorage.removeItem('cookieConsentSet')
      }
    }
    // Show banner if user has never made a choice or consent expired
    if (!consentSet || expired) {
      showBanner.value = true
    } else {
      showBanner.value = false
    }
  }
})

function acceptCookies() {
  localStorage.setItem('cookieConsent', 'true')
  localStorage.setItem('cookieConsentDate', new Date().toISOString())
  localStorage.setItem('cookieConsentSet', 'true')
  showBanner.value = false
}

function declineCookies() {
  localStorage.setItem('cookieConsent', 'false')
  localStorage.setItem('cookieConsentDate', new Date().toISOString())
  localStorage.setItem('cookieConsentSet', 'true')
  showBanner.value = false
}
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  background: var(--color-cold-cream);
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  box-shadow: 0 -1px 1px var(--color-cold-gray);
}
</style>
