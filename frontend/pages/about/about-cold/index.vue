<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <UCard class="cold-ucard">
        <SectionNav />
        <!-- Main Content -->
        <div
          class="main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <ContentDoc path="/about_cold" />
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import SectionNav from '@/components/layout/SectionNav.vue'

import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

onMounted(async () => {
  const route = useRoute()
  if (route.hash) {
    await nextTick()
    const el = document.querySelector(route.hash)
    if (el) {
      el.scrollIntoView({ behavior: 'auto' })
    }
  }
})
</script>

<style scoped>
::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}
</style>
