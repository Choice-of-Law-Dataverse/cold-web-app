<template>
  <main class="flex-1 mt-12 px-6">
    <div
      class="mx-auto min-h-[50vh] flex flex-col justify-center items-center text-center"
      style="max-width: var(--container-width); width: 100%"
    >
      <h2>{{ confirmationMessage }}</h2>

      <div class="mt-6 flex flex-col gap-2">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to">
          {{ link.text }}
        </NuxtLink>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const confirmationMessage =
  route.query.message || 'We have received your submission.'

let links = [
  { text: 'Take me back to Home', to: '/' },
  {
    text: 'Submit a new International Instrument',
    to: '/international-instrument/new',
  },
]
if (route.query.links) {
  try {
    const parsed = JSON.parse(route.query.links)
    if (Array.isArray(parsed)) {
      links = parsed.filter((l) => l && l.text && l.to)
    }
  } catch (e) {
    // ignore, fallback to default
  }
}
</script>

<script>
export default {
  layout: 'default',
}
</script>
