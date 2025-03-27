<template>
  <BackButton />

  <NotificationBanner
    v-if="
      shouldShowBanner &&
      (props.resultData?.Name || props.resultData?.['Jurisdictions'])
    "
    :jurisdictionName="
      props.resultData?.Name || props.resultData?.['Jurisdictions']
    "
  />

  <UCard class="cold-ucard">
    <!-- Header section -->
    <template #header v-if="showHeader">
      <UCardHeader
        v-if="resultData"
        :resultData="resultData"
        :cardType="formattedSourceTable"
        :showOpenLink="false"
        :formattedJurisdiction="formattedJurisdiction"
        :formattedTheme="formattedTheme"
      />
    </template>

    <!-- Main content -->
    <div class="flex">
      <div v-if="loading" class="py-8 px-6">Loading...</div>
      <div
        v-else
        class="main-content prose -space-y-10 flex flex-col gap-12 py-8 px-6 w-full"
      >
        <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
        <div
          v-for="(item, index) in keyLabelPairs"
          :key="index"
          class="flex flex-col"
        >
          <!-- Check if it's the special 'Specialist' key -->
          <template v-if="item.key === 'Specialist'">
            <slot></slot>
          </template>
          <template v-else>
            <!-- Conditionally render the label -->
            <p
              v-if="item.key !== 'Legal provisions IDs'"
              class="label-key -mb-1"
            >
              {{ item.label }}
            </p>
            <!-- Dynamic slot with kebab-case conversion -->
            <template
              v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]"
              :slot="item.key.replace(/ /g, '-').toLowerCase()"
            >
              <slot
                :name="item.key.replace(/ /g, '-').toLowerCase()"
                :value="resultData?.[item.key]"
              />
            </template>

            <template v-else>
              <p
                :class="[
                  props.valueClassMap[item.key] || 'text-gray-800',
                  'text-sm leading-relaxed whitespace-pre-line',
                ]"
              >
                {{ resultData?.[item.key] || 'N/A' }}
              </p>
            </template>
          </template>
        </div>
        <slot name="search-links"></slot>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRoute } from 'vue-router'

import BackButton from '~/components/BackButton.vue'
import UCardHeader from '~/components/UCardHeader.vue'

// Props for reusability across pages
const props = defineProps({
  loading: Boolean,
  resultData: Object,
  keyLabelPairs: Array,
  valueClassMap: Object,
  formattedSourceTable: String, // Receive the hard-coded value from [id].vue
  showHeader: {
    type: Boolean,
    default: true, // Default to true so headers are shown unless explicitly disabled
  },
  formattedJurisdiction: { type: Array, required: false, default: () => [] },
  formattedTheme: { type: Array, required: false, default: () => [] },
})

const route = useRoute()
const isJurisdictionPage = route.path.startsWith('/jurisdiction/')
const isQuestionPage = route.path.startsWith('/question/')
const jurisdictionCode = ref(null)
const coveredJurisdictions = ref([])
const shouldShowBanner = ref(false)

watch(
  () => props.resultData,
  (newData) => {
    if (!newData) return

    const rawJurisdiction = isJurisdictionPage
      ? route.params.id
      : isQuestionPage
        ? newData['Jurisdictions Alpha-3 code'] || newData.JurisdictionCode
        : null

    jurisdictionCode.value =
      typeof rawJurisdiction === 'string' ? rawJurisdiction.toLowerCase() : null
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    const response = await fetch('/temp_answer_coverage.txt')
    const text = await response.text()

    coveredJurisdictions.value = text
      .split('\n')
      .map((code) => code.trim().toLowerCase())
  } catch (error) {
    console.error('Failed to fetch covered jurisdictions:', error)
  }
})

// Reactively update banner display once everything is ready
watchEffect(() => {
  if (
    (isJurisdictionPage || isQuestionPage) &&
    jurisdictionCode.value &&
    coveredJurisdictions.value.length > 0
  ) {
    shouldShowBanner.value = !coveredJurisdictions.value.includes(
      jurisdictionCode.value
    )
  }
  // console.log('Page:', route.path)
  // console.log('jurisdictionCode:', jurisdictionCode.value)
  // console.log('covered:', coveredJurisdictions.value)
  // console.log('shouldShowBanner?', shouldShowBanner.value)
  console.log('resultData', props.resultData)
  // console.log('jurisdictionCode.value', jurisdictionCode.value)
  console.log('jurisdictionCode:', jurisdictionCode.value)
  console.log('shouldShowBanner:', shouldShowBanner.value)
})
</script>

<style scoped>
.cold-ucard ::v-deep(.px-4) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.cold-ucard ::v-deep(.py-5) {
  padding-top: 16px !important;
  padding-bottom: 18px !important;
}

.cold-ucard ::v-deep(.sm\:px-6) {
  padding-left: 16px !important;
  padding-right: 16px !important;
}

.label-key {
  @extend .label;
  padding: 0;
}
</style>
