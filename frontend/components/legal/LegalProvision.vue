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
import { onMounted, watch, nextTick, computed } from 'vue'
import { useLegalProvision } from '~/composables/useLegalProvision'

const props = defineProps({
  provisionId: {
    type: String,
    required: true
  },
  class: {
    type: String,
    default: ''
  },
  textType: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:hasEnglishTranslation'])

const {
  title,
  content,
  loading,
  error,
  hasEnglishTranslation,
  showEnglish,
  anchorId,
  fetchProvisionDetails,
  updateContent,
} = useLegalProvision({
  provisionId: props.provisionId,
  textType: props.textType,
  onHasEnglishTranslationUpdate: (value) => emit('update:hasEnglishTranslation', value),
})

const customClass = computed(() => props.class || '')

const scrollToAnchor = async () => {
  if (window.location.hash === `#${anchorId.value}`) {
    await nextTick()
    const anchorElement = document.getElementById(anchorId.value)
    if (anchorElement) {
      anchorElement.scrollIntoView({ behavior: 'smooth' })
    }
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

watch(showEnglish, updateContent)
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
  display: block;
  margin-top: 50px;
}

.no-margin .anchor {
  margin-top: 0;
}
</style> 