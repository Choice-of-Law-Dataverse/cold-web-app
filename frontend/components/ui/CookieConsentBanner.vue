<template>
  <transition name="fade">
    <div v-if="showBanner" class="cookie-banner">
      <span>
        This website uses cookies to ensure you get the best experience.
        <a href="/disclaimer" target="_blank" class="cookie-link">Learn more</a
        >.
      </span>
      <button class="cookie-btn" @click="acceptCookies">Allow Cookies</button>
      <button class="cookie-btn cookie-btn-secondary" @click="declineCookies">
        Do not allow Cookies
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const showBanner = ref(false)

onMounted(() => {
  if (typeof window !== 'undefined') {
    showBanner.value = !localStorage.getItem('cookieConsent')
  }
})

function acceptCookies() {
  localStorage.setItem('cookieConsent', 'true')
  showBanner.value = false
}

function declineCookies() {
  localStorage.setItem('cookieConsent', 'false')
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
  background: var(--color-cold-cream, #fff0d9);
  color: var(--color-cold-night, #0f0035);
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.07);
  font-size: 1rem;
}
.cookie-link {
  color: var(--color-cold-purple, #6f4dfa);
  text-decoration: underline;
  margin-left: 6px;
}
.cookie-btn {
  background: var(--color-cold-purple, #6f4dfa);
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 18px;
  font-size: 1rem;
  cursor: pointer;
  margin-left: 18px;
  transition: background 0.2s;
}
.cookie-btn:hover {
  background: #5439c7;
}
.cookie-btn-secondary {
  background: #e0e0e0;
  color: var(--color-cold-night, #0f0035);
  margin-left: 0;
}
.cookie-btn-secondary:hover {
  background: #cccccc;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
