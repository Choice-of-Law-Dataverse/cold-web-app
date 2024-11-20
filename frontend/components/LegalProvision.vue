<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div :class="['legal-provision', customClass]">
        <p class="label-key">{{ title }}</p>
        <p class="result-value-small">{{ content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
  provisionId: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: '',
  }, // Accept dynamic classes
})

// Reactive state for title and content
const title = ref<string | null>(null)
const content = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Compute the final class
const customClass = computed(() => props.class)

// Fetch the provision details on mount
async function fetchProvisionDetails() {
  const payload = {
    table: 'Legal provisions',
    id: props.provisionId,
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }
    )

    if (!response.ok)
      throw new Error(`Failed to fetch provision: ${props.provisionId}`)

    const data = await response.json()
    title.value = data.Article || 'Unknown Article'
    content.value =
      data['Full text of the provision (Original language)'] ||
      'No content available'
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProvisionDetails()
})
</script>

<style scoped>
.label-key {
  margin-top: 50px;
}

.no-margin .label-key {
  margin-top: 0;
}
</style>
