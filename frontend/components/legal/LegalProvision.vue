<template>
  <BaseLegalContent
    :title="displayTitle"
    :anchorId="anchorId"
    :class="class"
    :loading="loading"
    :error="error"
  >
    <template #header-actions>
      <div v-if="hasEnglishTranslation" class="flex items-center gap-1">
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
    </template>

    {{ content }}
  </BaseLegalContent>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useLegalProvision } from '~/composables/useLegalProvision'
import BaseLegalContent from './BaseLegalContent.vue'

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

const displayTitle = computed(() => {
  if (loading.value) return 'Loading...'
  if (error.value) return 'Error'
  return title.value || props.provisionId
})

// Fetch provision details when component is mounted
onMounted(() => {
  fetchProvisionDetails()
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
.label-key-provision-toggle {
  @apply text-sm text-gray-600;
}
</style> 