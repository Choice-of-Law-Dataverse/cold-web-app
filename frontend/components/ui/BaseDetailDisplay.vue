<template>
  <BackButton v-if="!hideBackButton" />

  <NotificationBanner
    v-if="showNotificationBanner"
    :notificationBannerMessage="notificationBannerMessage"
    :fallbackMessage="fallbackMessage"
    :icon="icon"
  />

  <NotificationBanner
    v-else-if="
      shouldShowBanner &&
      (props.resultData?.Name || props.resultData?.['Jurisdictions'])
    "
    :jurisdictionName="
      props.resultData?.Name || props.resultData?.['Jurisdictions']
    "
    :fallbackMessage="fallbackMessage"
    :icon="icon"
  />

  <template v-if="loading">
    <LoadingCard />
  </template>
  <template v-else>
    <UCard class="cold-ucard">
      <!-- Header section: always render, but pass headerMode -->
      <template #header>
        <BaseCardHeader
          :resultData="resultData"
          :cardType="formattedSourceTable"
          :showSuggestEdit="showSuggestEdit"
          :showOpenLink="showOpenLink"
          :formattedJurisdiction="formattedJurisdiction"
          :formattedTheme="formattedTheme"
          :headerMode="headerMode"
          @save="$emit('save')"
          @open-save-modal="$emit('open-save-modal')"
          @open-cancel-modal="$emit('open-cancel-modal')"
        >
          <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
            <slot :name="name" v-bind="slotData" />
          </template>
        </BaseCardHeader>
      </template>

      <!-- Main content -->
      <div class="flex">
        <div
          class="main-content prose -space-y-10 flex flex-col gap-8 py-8 px-6 w-full"
        >
          <!-- Render custom slot content (e.g., form fields) before keyLabelPairs -->
          <slot />
          <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
          <section
            v-for="(item, index) in keyLabelPairs"
            :key="index"
            class="section-gap p-0 m-0 flex flex-col"
          >
            <!-- Check if it's the special 'Specialist' key -->
            <template v-if="item.key === 'Region'">
              <slot></slot>
            </template>
            <!-- Check for slot first -->
            <template v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]">
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
                  <!-- Add this line to support header-actions slot for each section -->
                  <slot
                    :name="item.key + '-header-actions'"
                    :value="resultData?.[item.key]"
                  />
                  <!-- Render InfoTooltip if tooltip is defined in config -->
                  <template v-if="item.tooltip">
                    <InfoTooltip :text="item.tooltip" />
                  </template>
                </p>
                <!-- Conditionally render bullet list if Answer or Specialists is an array -->
                <template
                  v-if="
                    (item.key === 'Answer' || item.key === 'Specialists') &&
                    Array.isArray(getDisplayValue(item, resultData?.[item.key]))
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
          </section>
          <slot name="search-links"></slot>
        </div>
      </div>
    </UCard>
  </template>
</template>

<script setup>
import { useRoute } from 'vue-router'

import BackButton from '@/components/ui/BackButton.vue'
import BaseCardHeader from '@/components/ui/BaseCardHeader.vue'
import NotificationBanner from '@/components/ui/NotificationBanner.vue'
import LoadingCard from '@/components/layout/LoadingCard.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'

// Tooltips for Question Page
import tooltipQuestion from '@/content/info_boxes/question/question.md?raw'
import tooltipAnswer from '@/content/info_boxes/question/answer.md?raw'

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
  hideBackButton: {
    type: Boolean,
    default: false,
  },
  headerMode: {
    type: String,
    default: 'default',
  },
  showNotificationBanner: Boolean,
  notificationBannerMessage: String,
  fallbackMessage: String,
  icon: String,
})

const emit = defineEmits(['save', 'open-save-modal', 'open-cancel-modal'])

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
  // Use valueTransform if present
  if (item.valueTransform) {
    return item.valueTransform(value)
  }
  // For "Answer" and "Specialists", split by comma if a string contains commas.
  if (
    (item.key === 'Answer' || item.key === 'Specialists') &&
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
