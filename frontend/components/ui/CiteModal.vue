<template>
  <UModal
    :model-value="modelValue"
    @update:model-value="(v) => $emit('update:modelValue', v)"
    :ui="{ rounded: 'rounded-none' }"
  >
    <div class="p-6">
      <h2 class="mb-4">Cite This Page</h2>
      <p class="result-value-small-citation leading-relaxed break-words">
        {{ citationText }}
      </p>
      <div class="mt-2">
        <NuxtLink
          :to="route.fullPath"
          class="link-button no-underline !mb-2"
          :aria-disabled="copying ? 'true' : 'false'"
          @click.prevent="!copying && copyToClipboard()"
        >
          {{ copied ? 'Copied' : 'Copy to Clipboard' }}
          <UIcon
            :name="
              copied
                ? 'i-material-symbols:check-circle-outline'
                : 'i-material-symbols:content-copy-outline'
            "
            class="inline-block relative top-[1px]"
          />
        </NuxtLink>
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  // Optional override if you want to pass a known title directly
  title: { type: String, default: '' },
})
defineEmits(['update:modelValue'])

const route = useRoute()

const pageTitle = ref('')
const currentURL = ref('')
let titleObserver
const copied = ref(false)
const copying = ref(false)

onMounted(() => {
  // Safely access browser APIs on client
  pageTitle.value = typeof document !== 'undefined' ? document.title || '' : ''
  currentURL.value = typeof window !== 'undefined' ? window.location.href : ''

  // Observe <title> changes so we react if another component updates it later
  if (
    typeof window !== 'undefined' &&
    typeof MutationObserver !== 'undefined'
  ) {
    const titleEl = document.querySelector('title')
    if (titleEl) {
      titleObserver = new MutationObserver(() => {
        pageTitle.value = document.title || ''
      })
      titleObserver.observe(titleEl, {
        subtree: true,
        characterData: true,
        childList: true,
      })
    }
  }
})

onBeforeUnmount(() => {
  if (titleObserver) {
    titleObserver.disconnect()
    titleObserver = undefined
  }
})

function slugToPageType(slug) {
  switch (slug) {
    case 'jurisdiction':
      return 'Country Report'
    case 'court-decision':
      return 'Court Decision'
    case 'domestic-instrument':
      return 'Domestic Instrument'
    case 'regional-instrument':
      return 'Regional Instrument'
    case 'international-instrument':
      return 'International Instrument'
    case 'arbitral-rule':
      return 'Arbitral Rule'
    case 'arbitral-award':
      return 'Arbitral Award'
    case 'literature':
      return 'Literature'
    case 'question':
      return 'Question'
    default: {
      // Generic title-case fallback
      if (!slug) return 'Page'
      return slug
        .split('-')
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join(' ')
    }
  }
}

const pageType = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  return slugToPageType(segments[0] || '')
})

const year = computed(() => new Date().getFullYear())
const monthYear = computed(() => {
  const d = new Date()
  const month = d.toLocaleString('en-US', { month: 'long' })
  return `${month} ${d.getFullYear()}`
})

const citationText = computed(() => {
  // Pick provided prop title when available, else current document.title
  const rawTitle = (props.title && props.title.trim()) || pageTitle.value || ''
  // Remove trailing "— CoLD" or "- CoLD" (with or without surrounding spaces)
  let raw = rawTitle
  const cleaned = raw.replace(/[\s\u00A0]*[\u2014\-][\s\u00A0]*CoLD\s*$/i, '')
  // If title ends up being only "CoLD" (or blank), fall back to site name
  const normalized = cleaned.trim()
  const title =
    normalized && !/^CoLD$/i.test(normalized)
      ? normalized
      : 'Choice of Law Dataverse'
  const url = currentURL.value
  return `${title}. Choice of Law Dataverse (${year.value}). ${pageType.value} (${monthYear.value}). Licensed under CC BY-SA. Available at: ${url}`
})

async function copyToClipboard() {
  if (copying.value) return
  copying.value = true
  const text = citationText.value
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      // Fallback
      const ta = document.createElement('textarea')
      ta.value = text
      ta.setAttribute('readonly', '')
      ta.style.position = 'absolute'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  } catch (e) {
    // no-op; keep silent per UX
  } finally {
    copying.value = false
  }
}
</script>
