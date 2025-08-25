<template>
  <div>
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <div :id="anchorId" :class="['legal-content', customClass]">
        <div class="flex justify-between items-baseline mb-4">
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <!-- Caret toggle button -->
            <button
              type="button"
              class="p-1 rounded focus:outline-none focus:ring-2 focus:ring-gray-300 hover:bg-gray-100 transition-colors"
              :aria-controls="`${anchorId}-content`"
              :aria-expanded="isOpen.toString()"
              aria-label="Toggle content"
              @click="toggleOpen"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                class="h-4 w-4 transition-transform"
                :class="{ 'rotate-90': isOpen }"
              >
                <path
                  fill-rule="evenodd"
                  d="M7.293 14.707a1 1 0 0 1 0-1.414L10.586 10 7.293 6.707a1 1 0 1 1 1.414-1.414l4 4a1 1 0 0 1 0 1.414l-4 4a1 1 0 0 1-1.414 0Z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>

            <!-- Title / anchor link -->
            <a
              :href="`#${anchorId}`"
              class="label-key-provision-article anchor flex-1 min-w-0"
            >
              {{ displayTitle }}
            </a>
          </div>
          <slot name="header-actions" />
        </div>

        <div class="content-body" :id="`${anchorId}-content`" v-show="isOpen">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
    default: 'Loading...',
  },
  anchorId: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

const customClass = computed(() => props.class || '')
const displayTitle = computed(() => (props.loading ? '' : props.title || ''))

// Collapsible state (hidden by default)
const isOpen = ref(false)
const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const scrollToAnchor = async () => {
  const hash = window.location.hash.slice(1) // Remove the # symbol
  if (hash === props.anchorId) {
    // If navigated directly via hash, auto-expand for visibility
    isOpen.value = true
    await nextTick()
    const anchorElement = document.getElementById(hash)
    if (anchorElement) {
      anchorElement.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

onMounted(scrollToAnchor)
</script>

<style scoped>
.label-key-content {
  margin-top: 50px;
}

.no-margin .label-key-content {
  margin-top: 0;
}

.anchor {
  text-decoration: none;
  color: var(--color-cold-night) !important;
  display: block;
  margin-top: 50px;
}

.no-margin .anchor {
  margin-top: 0;
}

.content-body {
  font-size: 14px !important;
  font-weight: 400 !important;
  white-space: pre-line;
  word-wrap: break-word;
  word-break: break-word;
}
</style>
