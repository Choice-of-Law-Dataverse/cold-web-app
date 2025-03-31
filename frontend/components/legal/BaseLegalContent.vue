<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div :id="anchorId" :class="['legal-content', customClass]">
        <div class="flex justify-between items-baseline mb-4">
          <a
            :href="`#${anchorId}`"
            class="label-key-provision-article anchor flex-1 min-w-0"
          >
            {{ displayTitle }}
          </a>
          <slot name="header-actions" />
        </div>

        <div class="content-body">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
    default: 'Loading...'
  },
  anchorId: {
    type: String,
    required: true
  },
  class: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

const customClass = computed(() => props.class || '')
const displayTitle = computed(() => props.title || 'Loading...')

const scrollToAnchor = async () => {
  const hash = window.location.hash.slice(1) // Remove the # symbol
  if (hash === props.anchorId) {
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
  line-height: 26px !important;
  white-space: pre-line;
  word-wrap: break-word;
  word-break: break-word;
}
</style> 