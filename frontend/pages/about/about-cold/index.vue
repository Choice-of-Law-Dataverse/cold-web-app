<template>
  <ContentPageLayout>
    <ContentDoc path="/about_cold" />
  </ContentPageLayout>
</template>

<script setup>
import ContentPageLayout from '@/components/layout/ContentPageLayout.vue'
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
