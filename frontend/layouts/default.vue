<template>
  <div class="bg-cold-bg min-h-screen flex flex-col">
    <Nav />

    <main class="flex-1 mt-12">
      <NuxtPage />
    </main>

    <Footer />
    <CookieConsentBanner />
  </div>
</template>

<script setup>
import Nav from '@/components/layout/Nav.vue'
import Footer from '@/components/layout/Footer.vue'
import CookieConsentBanner from '@/components/ui/CookieConsentBanner.vue'
</script>
