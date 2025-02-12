<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div :id="anchorId" :class="['legal-provision', customClass]">
        <!-- Anchor for the article title -->
        <a :href="`#${anchorId}`" class="label-key anchor">
          {{ title }}
        </a>
        <p class="result-value-small">{{ content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'

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

const config = useRuntimeConfig()

// Compute the final class
const customClass = computed(() => props.class)

const anchorId = computed(() => {
  const articleNumber = title.value
    ? title.value.replace(/\s+/g, '')
    : props.provisionId.replace(/\s+/g, '')
  return articleNumber
})

const scrollToAnchor = async () => {
  if (window.location.hash === `#${anchorId.value}`) {
    // Wait for the DOM to render the component
    await nextTick()
    const anchorElement = document.getElementById(anchorId.value)
    if (anchorElement) {
      anchorElement.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

// Fetch the provision details on mount
async function fetchProvisionDetails() {
  const payload = {
    table: 'Legal provisions',
    id: props.provisionId,
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

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
  fetchProvisionDetails().then(scrollToAnchor)
})
</script>

<style scoped>
.label-key {
  margin-top: 50px;
}

.no-margin .label-key {
  margin-top: 0;
}

.anchor {
  text-decoration: none;
  color: var(--color-cold-night) !important;
  display: block; /* Ensure the anchor behaves like a block element */
  margin-top: 50px; /* Reapply the margin directly to the anchor */
}

.no-margin .anchor {
  margin-top: 0; /* Remove the margin for the first item */
}
</style>
