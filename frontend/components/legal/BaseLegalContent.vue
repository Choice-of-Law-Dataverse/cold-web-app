<template>
  <div
    ref="rootEl"
    class="base-legal-content"
    :class="{ 'is-first': isFirstProvision }"
  >
    <div v-if="error">{{ error }}</div>
    <div v-else>
      <div :id="anchorId" :class="['legal-content', customClass]">
        <div class="no-margin mb-4 flex items-center justify-between">
          <div class="flex min-w-0 flex-1 items-center gap-2">
            <!-- Caret toggle button -->
            <button
              type="button"
              class="rounded py-1 pl-[0.025rem] pr-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-300"
              :aria-controls="`${anchorId}-content`"
              :aria-expanded="isOpen.toString()"
              aria-label="Toggle content"
              @click="toggleOpen"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width="16"
                height="16"
                fill="none"
                :style="{
                  color: 'var(--color-cold-purple)',
                  transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)',
                }"
              >
                <path
                  d="M9 6l6 6-6 6"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="square"
                  stroke-linejoin="square"
                />
              </svg>
            </button>

            <!-- Title / anchor link -->
            <a
              :href="`#${anchorId}`"
              class="label-key-provision-article anchor min-w-0 flex-1"
              @click="onTitleClick"
            >
              {{ displayTitle }}
            </a>
          </div>
          <slot v-if="isOpen" name="header-actions" />
        </div>

        <div v-show="isOpen" :id="`${anchorId}-content`" class="content-body">
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
    required: false,
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

// Open content when clicking the title (preserve anchor navigation)
const onTitleClick = () => {
  isOpen.value = true
}

// Determine if this is the first provision instance in the container
const rootEl = ref(null)
const isFirstProvision = ref(false)
const evaluateIsFirst = () => {
  const el = rootEl.value
  const parent = el?.parentElement
  if (!el || !parent) {
    isFirstProvision.value = false
    return
  }
  // Find the first BaseLegalContent under the same parent in DOM order
  const firstBase = parent.querySelector('.base-legal-content')
  isFirstProvision.value = firstBase === el
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

onMounted(() => {
  evaluateIsFirst()
  scrollToAnchor()
})
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

/* Add spacing between provision component instances */
.base-legal-content {
  margin-top: 16px; /* default spacing between items */
}
</style>
