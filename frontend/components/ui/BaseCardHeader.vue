<template>
  <div
    class="header-container flex items-center justify-between mt-0.5"
    :key="formattedJurisdiction + formattedTheme + legalFamily"
  >
    <template v-if="cardType === 'Loading'"> </template>
    <template v-else>
      <!-- Left side of the header: Tags -->
      <div
        class="tags-container flex items-center overflow-x-auto scrollbar-hidden"
      >
        <!-- Display 'Name (from Jurisdiction)' or alternatives -->
        <NuxtLink
          v-for="(jurisdictionString, index) in formattedJurisdiction"
          :key="`jurisdiction-${index}`"
          class="label-jurisdiction cursor-pointer jurisdiction-label-link"
          :to="`/search?jurisdiction=${encodeURIComponent(jurisdictionString).replace(/%20/g, '+')}`"
        >
          <img
            v-if="!erroredImages[jurisdictionString]"
            :src="`https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${getJurisdictionISO(jurisdictionString)}.svg`"
            style="height: 9px"
            class="mr-1.5 mb-0.5"
            @error="handleImageError(erroredImages, jurisdictionString)"
          />
          {{ jurisdictionString }}
        </NuxtLink>
        <!-- Legal Family next to jurisdiction name -->
        <span
          v-for="(family, index) in legalFamily"
          :key="`legal-family-${index}`"
          class="label-theme"
        >
          {{ family }}
        </span>
        <!-- Display 'source_table' or a type selector when in 'new' mode -->
        <template v-if="adjustedSourceTable">
          <!-- In 'new' mode, show a simple dropdown to switch data type -->
          <select
            v-if="headerMode === 'new'"
            v-model="selectedType"
            class="border border-gray-300 px-2 pr-8 py-2 text-xs font-bold uppercase mr-3 min-w-[240px]"
          >
            <option v-for="type in typeOptions" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
          <!-- In other modes, keep the clickable label linking to search -->
          <NuxtLink
            v-else
            :to="
              '/search?type=' +
              encodeURIComponent(
                getSourceTablePlural(adjustedSourceTable)
              ).replace(/%20/g, '+')
            "
            :class="[
              'label',
              labelColorClass,
              'cursor-pointer',
              'source-table-label-link',
            ]"
          >
            {{ adjustedSourceTable }}
          </NuxtLink>
        </template>

        <!-- Display 'Themes' -->
        <NuxtLink
          v-for="(theme, index) in formattedTheme"
          :key="`theme-${index}`"
          class="label-theme cursor-pointer theme-label-link"
          :to="
            '/search?theme=' + encodeURIComponent(theme).replace(/%20/g, '+')
          "
        >
          {{ theme }}
        </NuxtLink>
      </div>

      <!-- Fade-out effect -->
      <div class="fade-out" :class="fadeOutClasses"></div>

      <!-- Right side of the header: Show either "Suggest Edit"/"Open" or custom for 'new' mode -->
      <div class="open-link ml-4">
        <template v-if="headerMode === 'new'">
          <UButton
            class="mr-2"
            color="gray"
            variant="outline"
            @click="$emit('open-cancel-modal')"
            >Cancel</UButton
          >
          <UButton color="primary" @click="$emit('open-save-modal')"
            >Submit</UButton
          >
        </template>
        <template v-else>
          <template v-if="showSuggestEdit">
            <div class="flex items-center space-x-5 label">
              <!-- All actions except the International Instrument Edit link -->
              <NuxtLink
                v-for="(action, index) in suggestEditActions.filter(
                  (a) =>
                    !(
                      props.cardType === 'International Instrument' &&
                      a.label === 'Edit'
                    )
                )"
                :key="index"
                class="flex items-center"
                :class="action.class"
                v-bind="action.to ? { to: action.to } : {}"
                target="_blank"
                rel="noopener noreferrer"
              >
                <template v-if="action.label === 'Cite'">
                  <UTooltip
                    :text="availableSoon"
                    :popper="{ placement: 'top' }"
                    :ui="{
                      background: 'bg-cold-night',
                      color: 'text-white',
                      base: 'pt-3 pr-3 pb-3 pl-3 normal-case whitespace-normal h-auto',
                      rounded: 'rounded-none',
                      ring: '',
                    }"
                  >
                    <span class="flex items-center">
                      {{ action.label }}
                      <UIcon
                        :name="action.icon"
                        class="inline-block ml-1 text-[1.2em] mb-0.5"
                      />
                    </span>
                  </UTooltip>
                </template>
                <template v-else>
                  {{ action.label }}
                  <UIcon
                    :name="action.icon"
                    class="inline-block ml-1 text-[1.2em] mb-0.5"
                  />
                </template>
              </NuxtLink>
              <!-- The Edit link for International Instrument only, no target/rel -->
              <NuxtLink
                v-for="(action, index) in suggestEditActions.filter(
                  (a) =>
                    props.cardType === 'International Instrument' &&
                    a.label === 'Edit'
                )"
                :key="'edit-' + index"
                class="flex items-center"
                :class="action.class"
                v-bind="action.to ? { to: action.to } : {}"
              >
                <template v-if="action.label === 'Cite'">
                  <UTooltip
                    :text="availableSoon"
                    :popper="{ placement: 'top' }"
                    :ui="{
                      background: 'bg-cold-night',
                      color: 'text-white',
                      base: 'pt-3 pr-3 pb-3 pl-3 normal-case whitespace-normal h-auto',
                      rounded: 'rounded-none',
                      ring: '',
                    }"
                  >
                    <span class="flex items-center">
                      {{ action.label }}
                      <UIcon
                        :name="action.icon"
                        class="inline-block ml-1 text-[1.2em] mb-0.5"
                      />
                    </span>
                  </UTooltip>
                </template>
                <template v-else>
                  {{ action.label }}
                  <UIcon
                    :name="action.icon"
                    class="inline-block ml-1 text-[1.2em] mb-0.5"
                  />
                </template>
              </NuxtLink>
            </div>
          </template>
          <template v-else>
            <NuxtLink :to="getLink()" class="label">
              Open
              <UIcon
                name="i-material-symbols:play-arrow"
                class="inline-block -mb-[1px]"
            /></NuxtLink>
          </template>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import jurisdictionsData from '@/assets/jurisdictions-data.json'
import { handleImageError } from '@/utils/handleImageError'

import availableSoon from '@/content/available_soon.md?raw'

const route = useRoute()
const router = useRouter()
const pdfExists = ref(false)
const isOpen = ref(false)
const isSaveOpen = ref(false)

const downloadPDFLink = computed(() => {
  const segments = route.path.split('/').filter(Boolean) // removes empty parts from path like ['', 'court-decision', 'CD-ARE-1128']
  const contentType = segments[0] || 'unknown' // e.g., 'court-decision'
  const id = segments[1] || '' // e.g., 'CD-ARE-1128'
  // If your Azure folders always follow the plural of the content type
  const folder = `${contentType}s`
  return `https://choiceoflawdataverse.blob.core.windows.net/${folder}/${id}.pdf`
})

// Props
const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
  cardType: {
    type: String,
    required: true,
  },
  showSuggestEdit: {
    type: Boolean,
    default: true,
  },
  showOpenLink: {
    type: Boolean,
    default: true,
  },
  formattedJurisdiction: {
    type: Array,
    required: false,
    default: () => [],
  },
  formattedTheme: {
    type: Array,
    required: false,
    default: () => [],
  },
  headerMode: {
    type: String,
    default: 'default',
  },
})

// Computed property for "jurisdiction" to handle multiple field options and duplicates
const formattedJurisdiction = computed(() => {
  if (props.formattedJurisdiction.length > 0) {
    return props.formattedJurisdiction
  }
  const jurisdictionString =
    props.resultData['Jurisdiction name'] ||
    props.resultData['Jurisdiction Names'] ||
    props.resultData['Name (from Jurisdiction)'] ||
    props.resultData['Jurisdiction'] ||
    props.resultData['Jurisdictions'] ||
    props.resultData['Instrument'] ||
    ''

  if (!jurisdictionString) {
    return [] // Return an empty array if no jurisdiction is found
  }

  // Split by comma, trim each item, and remove duplicates
  return [...new Set(jurisdictionString.split(',').map((item) => item.trim()))]
})

// Display `cardType` if available, or use `resultData.source_table`
const formattedSourceTable = computed(() => {
  return props.cardType || props.resultData?.source_table || ''
})

const adjustedSourceTable = computed(() => {
  // Use the result from `formattedSourceTable` and apply label adjustments
  switch (formattedSourceTable.value) {
    case 'Court Decisions':
      return 'Court Decision'
    case 'Answers':
      return 'Question'
    case 'Domestic Instrument':
      return 'Domestic Instrument'
    case 'Literature':
      return 'Literature'
    // Add more adjustments as needed
    default:
      return formattedSourceTable.value || '' // Fallback if no match
  }
})

const labelColorClass = computed(() => {
  switch (formattedSourceTable.value) {
    case 'Court Decisions':
      return 'label-court-decision'
    case 'Answers':
    case 'Question':
      return 'label-question'
    case 'Domestic Instrument':
    case 'Regional Instrument':
    case 'International Instrument':
      return 'label-domestic-instrument'
    case 'Literature':
      return 'label-literature'
    default:
      return '' // No color for unknown labels
  }
})

function labelClassForType(label) {
  switch (label) {
    case 'Court Decision':
      return 'label-court-decision'
    case 'Question':
      return 'label-question'
    case 'Domestic Instrument':
    case 'Regional Instrument':
    case 'International Instrument':
      return 'label-domestic-instrument'
    case 'Literature':
      return 'label-literature'
    default:
      return 'label'
  }
}

const formattedTheme = computed(() => {
  if (props.formattedTheme.length > 0) {
    return props.formattedTheme
  }

  // Handle literature's Themes
  if (props.cardType === 'Literature' && props.resultData['Themes']) {
    return props.resultData['Themes'].split(',').map((theme) => theme.trim())
  }

  // Handle other types
  const themes =
    props.resultData['Title of the Provision'] ?? props.resultData.Themes

  if (!themes || themes === 'None') {
    return []
  }

  return [...new Set(themes.split(',').map((theme) => theme.trim()))]
})

const erroredImages = reactive({}) // new reactive object

// New computed property for fade-out classes
const fadeOutClasses = computed(() => ({
  'open-link-true': props.showOpenLink,
  'suggest-edit-true': props.showSuggestEdit,
  'open-link-false': !props.showOpenLink,
  'suggest-edit-false': !props.showSuggestEdit,
}))

// Action items in "Suggest Edit" area
const suggestEditActions = computed(() => {
  let linkUrl = ''
  let linkLabel = 'Link'
  if (props.cardType === 'Literature') {
    if (props.resultData['Open Access URL']) {
      linkUrl = props.resultData['Open Access URL']
      linkLabel = 'Open Access Link'
    } else {
      linkUrl = props.resultData['Url'] || ''
    }
  } else if (props.cardType === 'Court Decisions') {
    linkUrl = props.resultData['Official Source (URL)'] || ''
  } else if (props.cardType === 'Domestic Instrument') {
    linkUrl = props.resultData['Source (URL)'] || ''
  } else if (props.cardType === 'Regional Instrument') {
    linkUrl = props.resultData['URL'] || ''
  } else if (props.cardType === 'International Instrument') {
    linkUrl = props.resultData['URL'] || ''
  }
  const actions = []
  if (linkUrl) {
    actions.push({
      label: linkLabel,
      icon: 'i-material-symbols:open-in-new',
      to: linkUrl,
    })
  }
  actions.push({
    label: 'Cite',
    icon: 'i-material-symbols:verified-outline',
    class: 'gray-link',
  })
  if (pdfExists.value) {
    actions.push({
      label: 'PDF',
      icon: 'i-material-symbols:arrow-circle-down-outline',
      to: downloadPDFLink.value,
    })
  }
  // Adjust the Edit link for International Instrument page only
  let editLink = suggestEditLink.value
  if (props.cardType === 'International Instrument' && props.resultData?.ID) {
    editLink = `/international-instrument/${props.resultData.ID}/edit`
  }
  actions.push({
    label: 'Edit',
    icon: 'i-material-symbols:edit-square-outline',
    to: editLink,
  })
  return actions
})

// Methods
function getLink() {
  // Determine the correct link based on the card type and resultData
  switch (props.cardType) {
    case 'Answers':
      return `/question/${props.resultData.id}`
    case 'Court Decisions':
      return `/court-decision/${props.resultData.id}`
    case 'Domestic Instrument':
      return `/domestic-instrument/${props.resultData.id}`
    case 'Regional Instrument':
      return `/regional-instrument/${props.resultData.id}`
    case 'International Instrument':
      return `/international-instrument/${props.resultData.id}`
    case 'Literature':
      return `/literature/${props.resultData.id}`
    default:
      return '#'
  }
}

onMounted(async () => {
  const res = await $fetch('/api/check-pdf-exists', {
    query: { url: downloadPDFLink.value },
  })
  pdfExists.value = res.exists
})

const suggestEditLink = ref('')
const airtableFormID = 'appQ32aUep05DxTJn/pagmgHV1lW4UIZVXS/form'

onMounted(() => {
  const currentURL = window.location.href
  suggestEditLink.value = `https://airtable.com/${airtableFormID}?prefill_URL=${encodeURIComponent(currentURL)}&hide_URL=true`
})
function getJurisdictionISO(name) {
  const entry = jurisdictionsData.find((item) => item.name.includes(name))
  return entry ? entry.alternative[0].toLowerCase() : 'default'
}

// Add computed for legalFamily
const legalFamily = computed(() => {
  if (
    props.resultData &&
    (props.cardType === 'Jurisdiction' || props.resultData['Legal Family'])
  ) {
    const value = props.resultData['Legal Family'] || ''
    if (!value || value === 'N/A') return []
    return value
      .split(',')
      .map((f) => f.trim())
      .filter((f) => f)
  }
  return []
})

// Pluralize source table label for URL function
function getSourceTablePlural(label) {
  if (label === 'Court Decision') return 'Court Decisions'
  if (label === 'Domestic Instrument') return 'Domestic Instruments'
  if (label === 'Regional Instrument') return 'Regional Instruments'
  if (label === 'International Instrument') return 'International Instruments'
  if (label === 'Question') return 'Questions'
  return label
}

// Dropdown options for 'new' pages
const typeOptions = [
  'Court Decision',
  'Domestic Instrument',
  'Regional Instrument',
  'International Instrument',
  'Literature',
  'Question',
]
const selectedType = ref('')

// Keep dropdown in sync with current header label
watch(
  () => adjustedSourceTable.value,
  (val) => {
    if (props.headerMode === 'new') {
      selectedType.value = val || ''
    }
  },
  { immediate: true }
)

function typeToNewPath(label) {
  const slug =
    label === 'Court Decision'
      ? 'court-decision'
      : label === 'Domestic Instrument'
        ? 'domestic-instrument'
        : label === 'Regional Instrument'
          ? 'regional-instrument'
          : label === 'International Instrument'
            ? 'international-instrument'
            : label === 'Question'
              ? 'question'
              : 'literature'
  return `/${slug}/new`
}

// Navigate on selection change in 'new' mode
watch(selectedType, (val, old) => {
  if (props.headerMode === 'new' && val && val !== old) {
    router.push(typeToNewPath(val))
  }
})
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative; /* Ensure fade-out positions correctly */
}

/* Ensure horizontal scrolling for tags without a visible scrollbar */
.tags-container {
  overflow-x: auto;
  white-space: nowrap;
  flex-grow: 1; /* Ensures it takes up available space */
}

.fade-out-container {
  position: relative;
  flex-shrink: 0; /* Prevent it from shrinking */
  width: 50px; /* Match the width of the fade effect */
  margin-left: -50px; /* Align the fade-out right before the "Open" link */
  z-index: 1; /* Ensures it appears above the scrolling content */
}

/* Fade-out effect */
.fade-out {
  position: absolute;
  top: 0;
  right: 50px; /* Default: Positioned just before the right-aligned link */
  width: 60px;
  height: 100%;
  background: linear-gradient(to left, white, transparent);
  pointer-events: none;
  z-index: 10; /* Ensure it's above the scrolling tags */
}

/* Adjust position when only one of the links is shown */
.fade-out.open-link-true {
  right: 50px; /* Positioned before "Open" */
}

.fade-out.suggest-edit-true {
  right: 266px; /* Positioned before icons */
}

/* Ensures the fade-out is always correctly positioned */
.fade-out.open-link-false.suggest-edit-false {
  right: 0; /* Positioned at the edge of the container */
}

/* Right-aligned open link */
.open-link {
  flex-shrink: 0; /* Prevent shrinking */
  position: relative;
  z-index: 20; /* Ensure it's above the fade-out */
}

/* Hide the scrollbar for a cleaner look */
.scrollbar-hidden::-webkit-scrollbar {
  display: none; /* For Chrome, Safari, and Edge */
}
.scrollbar-hidden {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

.gray-link {
  color: var(--color-cold-night-alpha-25) !important;
}

a {
  font-weight: 600 !important;
}

/* Preserve label color for clickable jurisdiction links */
.jurisdiction-label-link {
  color: var(--color-cold-night) !important;
  font-weight: 700 !important;
}

.theme-label-link {
  color: var(--color-cold-night-alpha) !important;
  font-weight: 700 !important;
}

.source-table-label-link {
  font-weight: 700 !important;
}

/* Ensure NuxtLink.label-court-decision, etc. use the correct color even as a link */
.label-court-decision,
a.label-court-decision {
  color: var(--color-label-court-decision) !important;
}
.label-question,
a.label-question {
  color: var(--color-label-question) !important;
}
.label-domestic-instrument,
a.label-domestic-instrument {
  color: var(--color-label-domestic-instrument) !important;
}
.label-literature,
a.label-literature {
  color: var(--color-label-literature) !important;
}
</style>
