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

  <template v-if="loading">
    <LoadingCard />
  </template>
  <template v-else>
    <UCard class="cold-ucard">
      <!-- Header section -->
      <template #header v-if="showHeader">
        <BaseCardHeader
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
        <div
          class="main-content prose -space-y-10 flex flex-col gap-8 py-8 px-6 w-full"
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
              <!-- Check for slot first -->
              <template
                v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]"
              >
                <slot
                  :name="item.key.replace(/ /g, '-').toLowerCase()"
                  :value="resultData?.[item.key]"
                />
              </template>
              <!-- If no slot, use default display -->
              <template v-else>
                <!-- Conditionally render the label and value container -->
                <div
                  v-if="shouldDisplayValue(item, resultData?.[item.key])"
                  class="mb-6"
                >
                  <!-- Conditionally render the label -->
                  <p class="label-key mb-2.5 flex items-center">
                    {{ item.label }}
                    <!-- Add tooltip for specific labels -->
                    <template v-if="item.label === 'Question'">
                      <UTooltip
                        :text="tooltipQuestion"
                        :popper="{ placement: 'top' }"
                        :ui="{
                          background: 'bg-cold-night',
                          color: 'text-white',
                          base: 'pt-3 pr-3 pb-3 pl-3 normal-case whitespace-normal h-auto',
                          rounded: 'rounded-none',
                          ring: '',
                        }"
                      >
                        <span class="ml-1 cursor-pointer">
                          <Icon name="i-material-symbols:info-outline" />
                        </span>
                      </UTooltip>
                    </template>
                  </p>
                  <!-- Conditionally render bullet list if Answer is an array -->
                  <template
                    v-if="
                      item.key === 'Answer' &&
                      Array.isArray(
                        getDisplayValue(item, resultData?.[item.key])
                      )
                    "
                  >
                    <ul>
                      <li
                        v-for="(line, i) in getDisplayValue(
                          item,
                          resultData?.[item.key]
                        )"
                        :key="i"
                        :class="
                          props.valueClassMap[item.key] ||
                          'leading-relaxed whitespace-pre-line'
                        "
                      >
                        {{ line }}
                      </li>
                    </ul>
                  </template>
                  <template v-else>
                    <p
                      :class="[
                        props.valueClassMap[item.key] ||
                          'leading-relaxed whitespace-pre-line',
                        (!resultData?.[item.key] ||
                          resultData?.[item.key] === 'NA') &&
                        item.emptyValueBehavior?.action === 'display' &&
                        !item.emptyValueBehavior?.getFallback
                          ? 'text-gray-300'
                          : '',
                      ]"
                    >
                      {{ getDisplayValue(item, resultData?.[item.key]) }}
                    </p>
                  </template>
                </div>
              </template>
            </template>
          </div>
          <slot name="search-links"></slot>
        </div>
      </div>
    </UCard>
  </template>
</template>

<script setup>
import { useRoute } from 'vue-router'

import BackButton from '~/components/ui/BackButton.vue'
import BaseCardHeader from '~/components/ui/BaseCardHeader.vue'
import NotificationBanner from '~/components/ui/NotificationBanner.vue'
import LoadingCard from './components/layout/LoadingCard.vue'

import tooltipQuestion from '@/content/info_box_question.md?raw'

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
})

// Add these new functions
const shouldDisplayValue = (item, value) => {
  if (!item.emptyValueBehavior) return true
  if (
    item.emptyValueBehavior.shouldHide &&
    item.emptyValueBehavior.shouldHide(props.resultData)
  ) {
    return false
  }
  if (
    item.emptyValueBehavior.action === 'hide' &&
    (!value || value === 'NA' || value === 'N/A')
  ) {
    return false
  }
  return true
}

const getDisplayValue = (item, value) => {
  // New logic for the "Answer" field: if the value contains commas, split it.
  if (
    item.key === 'Answer' &&
    typeof value === 'string' &&
    value.includes(',')
  ) {
    return value.split(',').map((part) => part.trim())
  }
  if (!item.emptyValueBehavior) return value || 'N/A'
  if (
    (!value || value === 'NA') &&
    item.emptyValueBehavior.action === 'display'
  ) {
    if (item.emptyValueBehavior.getFallback) {
      return item.emptyValueBehavior.getFallback(props.resultData)
    }
    return item.emptyValueBehavior.fallback || 'N/A'
  }
  return value
}
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

.label-key span {
  display: inline-flex;
  align-items: center;
  margin-top: -1px;
  color: var(--color-cold-purple);
  font-size: 1.1em;
}
</style>
