<template>
  <div
    class="header-container flex items-center justify-between mt-0.5"
    :key="formattedJurisdiction + formattedTheme"
  >
    <template v-if="cardType === 'Loading'"> </template>
    <template v-else>
      <!-- Left side of the header: Tags -->
      <div
        class="tags-container flex items-center overflow-x-auto scrollbar-hidden"
      >
        <!-- Display 'Name (from Jurisdiction)' or alternatives -->
        <span
          v-for="(jurisdictionString, index) in formattedJurisdiction"
          :key="`jurisdiction-${index}`"
          class="label-jurisdiction"
        >
          <img
            v-if="!erroredImages[jurisdictionString]"
            :src="`https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${getJurisdictionISO(jurisdictionString)}.svg`"
            style="height: 9px"
            class="mr-1.5 mb-0.5"
            @error="handleImageError(erroredImages, jurisdictionString)"
          />
          {{ jurisdictionString }}
        </span>

        <!-- Display 'source_table' -->
        <span v-if="adjustedSourceTable" :class="['label', labelColorClass]">
          {{ adjustedSourceTable }}
        </span>

        <!-- Display 'Themes' -->
        <span
          v-for="(theme, index) in formattedTheme"
          :key="`theme-${index}`"
          class="label-theme"
        >
          {{ theme }}
        </span>
      </div>

      <!-- Fade-out effect -->
      <div class="fade-out" :class="fadeOutClasses"></div>

      <!-- Right side of the header: Show either "Suggest Edit" or "Open" -->
      <div class="open-link ml-4">
        <template v-if="showSuggestEdit">
          <div class="flex items-center space-x-5 label">
            <NuxtLink
              v-for="(action, index) in suggestEditActions"
              :key="index"
              class="flex items-center"
              :class="action.class"
              v-bind="action.to ? { to: action.to } : {}"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ action.label }}
              <UIcon
                :name="action.icon"
                class="inline-block ml-1 text-[1.2em] mb-0.5"
              />
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
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import jurisdictionsData from '../../assets/jurisdictions-data.json' // added import
import { handleImageError } from '../../utils/handleImageError'

const airtableFormID = 'appQ32aUep05DxTJn/pagmgHV1lW4UIZVXS/form'

// Computed property to generate the prefilled form URL with hidden field
const suggestEditLink = computed(() => {
  if (import.meta.server) return '#' // Prevent issues on SSR
  const currentPageURL = encodeURIComponent(window.location.href)
  return `https://airtable.com/${airtableFormID}?prefill_URL=${currentPageURL}&hide_URL=true`
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
    case 'Legal Instrument':
      return 'Legal Instrument'
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
    case 'Legal Instrument':
      return 'label-legal-instrument'
    case 'Literature':
      return 'label-literature'
    default:
      return '' // No color for unknown labels
  }
})

const formattedTheme = computed(() => {
  if (props.formattedTheme.length > 0) {
    return props.formattedTheme
  }

  // Handle literature's Manual Tags
  if (props.cardType === 'Literature' && props.resultData['Manual Tags']) {
    return props.resultData['Manual Tags']
      .split(';')
      .map((theme) => theme.trim())
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

// New computed property for action items in "Suggest Edit" area
const suggestEditActions = computed(() => [
  {
    label: 'Link',
    icon: 'i-material-symbols:language',
    to: 'https://example.net/',
  },
  {
    label: 'Cite',
    icon: 'i-material-symbols:verified-outline',
    class: 'gray-link',
  },
  {
    label: 'PDF',
    icon: 'i-material-symbols:arrow-circle-down-outline',
    to: 'https://choiceoflawdataverse.blob.core.windows.net/assets/dummy.pdf',
  },
  {
    label: 'Edit',
    icon: 'i-material-symbols:edit-square-outline',
    to: suggestEditLink.value,
  },
])

// Methods
function getLink() {
  // Determine the correct link based on the card type and resultData
  switch (props.cardType) {
    case 'Answers':
      return `/question/${props.resultData.id}`
    case 'Court Decisions':
      return `/court-decision/${props.resultData.id}`
    case 'Legal Instrument':
      return `/legal-instrument/${props.resultData.id}`
    case 'Literature':
      return `/literature/${props.resultData.id}`
    default:
      return '#'
  }
}

function getJurisdictionISO(name) {
  const entry = jurisdictionsData.find((item) => item.name.includes(name))
  return entry ? entry.alternative[0].toLowerCase() : 'default'
}
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
</style>
