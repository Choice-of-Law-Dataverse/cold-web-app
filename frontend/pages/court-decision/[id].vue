<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="modifiedCourtDecision"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Court Decisions"
  >
    <!-- Quote section with language toggle -->
    <template #Quote-header-actions>
      <div v-if="hasEnglishQuoteTranslation" class="flex items-center gap-1">
        <span
          class="label-key-provision-toggle mr-[-0px]"
          :class="{
            'opacity-25': showEnglishQuote,
            'opacity-100': !showEnglishQuote,
          }"
        >
          Original
        </span>
        <UToggle
          v-model="showEnglishQuote"
          size="2xs"
          class="bg-[var(--color-cold-gray)]"
        />
        <span
          class="label-key-provision-toggle"
          :class="{
            'opacity-25': !showEnglishQuote,
            'opacity-100': showEnglishQuote,
          }"
        >
          English
        </span>
      </div>
    </template>
    <template #Quote="{ value }">
      <span>
        {{
          showEnglishQuote && hasEnglishQuoteTranslation
            ? modifiedCourtDecision['Translated Excerpt']
            : value
        }}
      </span>
    </template>
    <template #related-questions>
      <RelatedQuestions
        :jurisdictionCode="
          modifiedCourtDecision['Jurisdictions Alpha-3 Code'] || ''
        "
        :questions="modifiedCourtDecision['Questions'] || ''"
        class="!mt-2"
      />
    </template>
    <template #related-literature>
      <RelatedLiterature
        :themes="themes"
        :valueClassMap="valueClassMap['Related Literature']"
        :useId="false"
        class="!mt-2"
      />
    </template>
  </BaseDetailLayout>

  <!-- Error Alert -->
  <UAlert
    v-if="error"
    type="error"
    class="mx-auto mt-4"
    style="max-width: var(--container-width)"
  >
    {{ error }}
  </UAlert>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import RelatedQuestions from '~/components/legal/RelatedQuestions.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { courtDecisionConfig } from '~/config/pageConfigs'
import { formatDate } from '~/utils/format.js'
// import UToggle from '~/components/ui/UToggle.vue'
import { ref } from 'vue'

const route = useRoute()
const router = useRouter()
const { loading, error, data: courtDecision, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig
)

// Debug the court decision data and configuration
watch(courtDecision, (newValue) => {
  if (newValue) {
  }
})

const themes = computed(() => {
  if (!courtDecision.value) return ''
  const themesData = courtDecision.value['Themes']
  return themesData || ''
})

const modifiedCourtDecision = computed(() => {
  if (!courtDecision.value) return null
  return {
    ...courtDecision.value,
    'Case Title':
      courtDecision.value['Case Title'] === 'Not found'
        ? courtDecision.value['Case Citation']
        : courtDecision.value['Case Title'],
    'Related Literature': themes.value,
    'Case Citation': courtDecision.value['Case Citation'],
    Questions: courtDecision.value['Questions'],
    'Jurisdictions Alpha-3 Code':
      courtDecision.value['Jurisdictions Alpha-3 Code'],
    'Publication Date ISO': formatDate(
      courtDecision.value['Publication Date ISO']
    ),
    'Date of Judgment': formatDate(courtDecision.value['Date of Judgment']),
  }
})

const showEnglishQuote = ref(false)
const hasEnglishQuoteTranslation = computed(() => {
  return !!(
    modifiedCourtDecision.value &&
    modifiedCourtDecision.value['Translated Excerpt'] &&
    modifiedCourtDecision.value['Translated Excerpt'].trim() !== ''
  )
})

const fetchCourtDecision = async () => {
  try {
    await fetchData({
      table: 'Court Decisions',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `Court decision not found` },
      })
    } else {
      console.error('Failed to fetch court decision:', err)
    }
  }
}

onMounted(() => {
  fetchCourtDecision()
})

// Refetch if the route ID changes
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchCourtDecision()
    }
  }
)
</script>

<style scoped>
.label-key-provision-toggle {
  @apply text-sm text-gray-600;
}
</style>
