<template>
  <div v-if="isEditPage">
    <div v-if="!loading">
      <UFormGroup size="lg" hint="Required" :error="errors.name">
        <template #label>
          <span class="label">Name</span>
        </template>
        <UInput
          v-model="name"
          class="mt-2"
          placeholder="Name of the International Instrument"
        />
      </UFormGroup>
    </div>
  </div>
  <div v-else>Page not found</div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { z } from 'zod'

const route = useRoute()
const isEditPage = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) && slug.length === 2 && slug[1] === 'edit'
})
const instrumentId = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) ? slug[0] : null
})

const loading = ref(true)
const name = ref('')
const errors = ref({})

const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: 'Name is required' })
    .min(3, { message: 'Name must be at least 3 characters long' }),
})

async function fetchInstrument() {
  console.log('fetchInstrument called, instrumentId:', instrumentId.value)
  loading.value = true
  try {
    if (!instrumentId.value) {
      loading.value = false
      return
    }
    // Use window.location.origin as fallback if runtime config is not available
    const apiBaseUrl =
      (typeof useRuntimeConfig === 'function'
        ? useRuntimeConfig().public.apiBaseUrl
        : '') || window.location.origin
    const fastApiKey =
      typeof useRuntimeConfig === 'function'
        ? useRuntimeConfig().public.FASTAPI
        : ''
    const response = await fetch(`${apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        authorization: `Bearer ${fastApiKey}`,
      },
      body: JSON.stringify({
        table: 'International Instruments',
        id: instrumentId.value,
      }),
    })
    console.log('Fetch response status:', response.status)
    const responseText = await response.text()
    console.log('Fetch response text:', responseText)
    if (!response.ok) throw new Error('Failed to fetch instrument')
    const data = JSON.parse(responseText)
    console.log('Fetched data:', data)
    name.value = data['Name'] || data['Title (in English)'] || ''
  } catch (err) {
    console.error('Fetch error:', err)
  } finally {
    loading.value = false
  }
}

watch(
  [isEditPage, instrumentId],
  ([edit, id]) => {
    console.log('watch triggered', { edit, id })
    if (edit && id) {
      fetchInstrument()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.label {
  font-weight: 600;
}
</style>
