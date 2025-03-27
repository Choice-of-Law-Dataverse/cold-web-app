<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div :id="anchorId" :class="['legal-provision', customClass]">
        <div class="flex justify-between items-baseline">
          <a
            :href="`#${anchorId}`"
            class="label-key-provision-article anchor flex-1 min-w-0"
          >
            {{ title }}
          </a>
          <div class="flex items-center gap-1" v-if="hasEnglishTranslation">
            <!-- Original label (fades when English is active) -->
            <span
              class="label-key-provision-toggle mr-[-0px]"
              :class="{
                'opacity-25': showEnglish,
                'opacity-100': !showEnglish,
              }"
            >
              Original
            </span>

            <UToggle
              v-model="showEnglish"
              size="2xs"
              class="bg-[var(--color-cold-gray)]"
            />

            <!-- English label (fades when Original is active) -->
            <span
              class="label-key-provision-toggle"
              :class="{
                'opacity-25': !showEnglish,
                'opacity-100': showEnglish,
              }"
            >
              English
            </span>
          </div>
        </div>

        <p class="result-value-small whitespace-pre-line">{{ content }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
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
  textType: {
    type: String,
    required: true,
  },
})

// Reactive state for title and content
const title = ref(null)
const content = ref(null)
const loading = ref(true)
const error = ref(null)

const config = useRuntimeConfig()

const hasEnglishTranslation = ref(false)
const emit = defineEmits(['update:hasEnglishTranslation'])
const showEnglish = ref(true)
const provisionData = ref(null) // Store provision details

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
    table: 'Domestic Legal Provisions',
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

    if (!response.ok) {
      throw new Error(`Failed to fetch provision: ${props.provisionId}`)
    }
    const data = await response.json()

    title.value = data.Article || 'Unknown Article'
    hasEnglishTranslation.value =
      'Full Text of the Provision (English Translation)' in data
    emit('update:hasEnglishTranslation', hasEnglishTranslation.value)

    provisionData.value = data // Store the fetched provision data

    // Set initial content to English first, then fallback to Original Language
    content.value = showEnglish.value
      ? data['Full Text of the Provision (English Translation)'] ||
        data['Full Text of the Provision (Original Language)'] ||
        'No content available'
      : data['Full Text of the Provision (Original Language)'] ||
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

watch(
  () => props.textType,
  () => {
    fetchProvisionDetails()
  }
)

watch(showEnglish, () => {
  if (provisionData.value) {
    content.value = showEnglish.value
      ? provisionData.value[
          'Full Text of the Provision (English Translation)'
        ] || 'No English translation available'
      : provisionData.value['Full Text of the Provision (Original Language)'] ||
        'No content available'
  }
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
