<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="Court Decision"
    :hideBackButton="true"
    headerMode="new"
    @open-save-modal="openSaveModal"
    @open-cancel-modal="showCancelModal = true"
    :showNotificationBanner="true"
    :notificationBannerMessage="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
  >
    <div class="section-gap p-0 m-0">
      <UFormGroup size="lg" hint="Required" :error="errors.case_citation">
        <template #label>
          <span class="label">Case citation</span>
          <InfoTooltip :text="tooltipCaseCitation" />
        </template>
        <UInput v-model="caseCitation" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" hint="Required" class="mt-8">
        <template #label>
          <span class="label">Publication Date</span>
          <InfoTooltip :text="tooltipPublicationDate" />
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="format(datePublication, 'dd MMMM yyyy')"
            class="mt-2"
          />
          <template #panel="{ close }">
            <DatePicker v-model="datePublication" is-required @close="close" />
          </template>
        </UPopover>
      </UFormGroup>

      <UFormGroup
        size="lg"
        hint="Required"
        class="mt-8"
        :error="errors.official_source_url"
      >
        <template #label>
          <span class="label">Official source (URL)</span>
        </template>
        <UInput v-model="officialSourceUrl" class="mt-2" />
      </UFormGroup>

      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.copyright_issues"
      >
        <template #label>
          <span class="label">Copyright issues</span>
        </template>
        <URadioGroup
          v-model="copyrightIssues"
          class="mt-2"
          :options="copyrightOptions"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Full Text</span>
        </template>
        <UTextarea
          v-model="caseFullText"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">English Translation of Full Text</span>
        </template>
        <UTextarea
          v-model="caseEnglishTranslation"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Case Rank</span>
        </template>
        <UInput v-model="caseRank" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Jurisdiction</span>
        </template>
        <SearchFilters
          :options="jurisdictionOptions"
          v-model="selectedJurisdiction"
          class="mt-2 w-full sm:w-auto"
          showAvatars="true"
          :multiple="false"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Abstract</span>
          <InfoTooltip :text="tooltipAbstract" />
        </template>
        <UTextarea
          v-model="caseAbstract"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Relevant Facts</span>
          <InfoTooltip :text="tooltipRelevantFacts" />
        </template>
        <UTextarea
          v-model="caseRelevantFacts"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">PIL Provisions</span>
          <InfoTooltip :text="tooltipPILProvisions" />
        </template>
        <UInput v-model="casePILProvisions" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Choice of Law Issue</span>
          <InfoTooltip :text="tooltipChoiceofLawIssue" />
        </template>
        <UTextarea
          v-model="caseChoiceofLawIssue"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Court's Position</span>
          <InfoTooltip :text="tooltipCourtsPosition" />
        </template>
        <UTextarea
          v-model="caseCourtsPosition"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Translated Excerpt</span>
        </template>
        <UTextarea
          v-model="caseTranslatedExcerpt"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Quote</span>
          <InfoTooltip :text="tooltipQuote" />
        </template>
        <UTextarea
          v-model="caseQuote"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Judgment Date</span>
          <InfoTooltip :text="tooltipJudgmentDate" />
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="format(dateJudgment, 'dd MMMM yyyy')"
            class="mt-2"
          />
          <template #panel="{ close }">
            <DatePicker v-model="dateJudgment" is-required @close="close" />
          </template>
        </UPopover>
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Case Title</span>
          <InfoTooltip :text="tooltipCaseTitle" />
        </template>
        <UInput v-model="caseTitle" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Instance</span>
          <InfoTooltip :text="tooltipInstance" />
        </template>
        <UInput v-model="caseInstance" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Official Keywords</span>
        </template>
        <UTextarea
          v-model="caseOfficialKeywords"
          class="mt-2 resize-y min-h-[140px]"
          :rows="6"
        />
      </UFormGroup>
    </div>
  </BaseDetailLayout>

  <CancelModal v-model="showCancelModal" @confirm-cancel="confirmCancel" />
  <SaveModal
    v-model="showSaveModal"
    :email="email"
    :comments="comments"
    :token="token"
    :saveModalErrors="saveModalErrors"
    :name="caseCitation"
    :specialists="specialists"
    :date="datePublication"
    :pdfFile="pdfFile"
    :link="officialSourceUrl"
    @update:email="(val) => (email = val)"
    @update:comments="(val) => (comments = val)"
    @update:token="(val) => (token = val)"
    @update:saveModalErrors="(val) => (saveModalErrors.value = val)"
    @save="handleNewSave"
  />
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useHead, useRouter } from '#imports'
import { z } from 'zod'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import DatePicker from '@/components/ui/DatePicker.vue'
import CancelModal from '@/components/ui/CancelModal.vue'
import SaveModal from '@/components/ui/SaveModal.vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import { format } from 'date-fns'

import tooltipAbstract from '@/content/info_boxes/court_decision/abstract.md?raw'
import tooltipCaseCitation from '@/content/info_boxes/court_decision/case_citation.md?raw'
import tooltipCaseTitle from '@/content/info_boxes/court_decision/case_title.md?raw'
import tooltipChoiceofLawIssue from '@/content/info_boxes/court_decision/choice_of_law_issue.md?raw'
import tooltipCourtsPosition from '@/content/info_boxes/court_decision/courts_position.md?raw'
import tooltipInstance from '@/content/info_boxes/court_decision/instance.md?raw'
import tooltipJudgmentDate from '@/content/info_boxes/court_decision/judgment_date.md?raw'
import tooltipPILProvisions from '@/content/info_boxes/court_decision/pil_provisions.md?raw'
import tooltipPublicationDate from '@/content/info_boxes/court_decision/publication_date.md?raw'
import tooltipQuote from '@/content/info_boxes/court_decision/quote.md?raw'
import tooltipRelevantFacts from '@/content/info_boxes/court_decision/relevant_facts.md?raw'

const config = useRuntimeConfig()

// Form data
const caseCitation = ref('')
const caseTitle = ref('')
// Newly added fields used by multi-line inputs
const caseFullText = ref('')
const caseEnglishTranslation = ref('')
const caseRank = ref('')
const caseAbstract = ref('')
const caseRelevantFacts = ref('')
const casePILProvisions = ref('')
const caseChoiceofLawIssue = ref('')
const caseCourtsPosition = ref('')
const caseTranslatedExcerpt = ref('')
const caseQuote = ref('')
const caseInstance = ref('')
const caseOfficialKeywords = ref('')
const officialSourceUrl = ref('')
const copyrightIssues = ref('No')
const datePublication = ref(new Date())
const dateJudgment = ref(new Date())

// Required by SaveModal (kept for parity with other pages)
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

// Ensure Submit button reactivity when token changes
watch(token, () => {})
// Jurisdiction select state and options (reuse SearchResults strategy)
const selectedJurisdiction = ref([])
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])

const loadJurisdictions = async () => {
  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table: 'Jurisdictions', filters: [] }),
      }
    )

    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const jurisdictionsData = await response.json()
    jurisdictionOptions.value = [
      { label: 'Select Jurisdiction' },
      ...jurisdictionsData
        .filter((entry) => entry['Irrelevant?'] === false)
        .map((entry) => ({
          label: entry.Name,
          avatar: entry['Alpha-3 Code']
            ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${entry['Alpha-3 Code'].toLowerCase()}.svg`
            : undefined,
        }))
        .sort((a, b) => (a.label || '').localeCompare(b.label || '')),
    ]
  } catch (error) {
    console.error('Error loading jurisdictions:', error)
  }
}

onMounted(loadJurisdictions)
// Radio options for Copyright issues
const copyrightOptions = [
  { value: 'No', label: 'No' },
  { value: 'Yes', label: 'Yes' },
]

// Validation schema
const formSchema = z.object({
  case_citation: z
    .string()
    .min(1, { message: 'Case citation is required' })
    .min(3, { message: 'Case citation must be at least 3 characters long' }),
  official_source_url: z.string().url({
    message: 'Link must be a valid URL. It must start with "https://"',
  }),
  jurisdiction: z
    .string()
    .min(1, { message: 'Please select a jurisdiction' })
    .optional(),
  copyright_issues: z.string().min(1, {
    message: 'Please specify copyright issues (e.g., none/unknown or describe)',
  }),
})

// Form validation state
const errors = ref({})
const saveModalErrors = ref({})

const router = useRouter()
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New Court Decision — CoLD' })

function validateForm() {
  try {
    const formData = {
      case_citation: caseCitation.value,
      official_source_url: officialSourceUrl.value,
      jurisdiction:
        (Array.isArray(selectedJurisdiction.value) &&
          selectedJurisdiction.value[0]?.label) ||
        undefined,
      copyright_issues: copyrightIssues.value,
    }
    formSchema.parse(formData)
    errors.value = {}
    return true
  } catch (error) {
    if (error instanceof z.ZodError) {
      errors.value = {}
      error.errors.forEach((err) => {
        errors.value[err.path[0]] = err.message
      })
    }
    return false
  }
}

function openSaveModal() {
  const isValid = validateForm()
  if (isValid) {
    showSaveModal.value = true
  }
}

function confirmCancel() {
  router.push('/')
}

function handleNewSave() {
  const payload = {
    case_citation: caseCitation.value,
    case_title: caseTitle.value || undefined,
    official_source_url: officialSourceUrl.value,
    date_publication: format(datePublication.value, 'yyyy-MM-dd'),
    jurisdiction:
      (Array.isArray(selectedJurisdiction.value) &&
        selectedJurisdiction.value[0]?.label) ||
      undefined,
    copyright_issues: copyrightIssues.value,
  }

  // Explicitly log the exact payload we send
  console.log('Submitting:', JSON.stringify(payload, null, 2))
  ;(async () => {
    try {
      await $fetch(`${config.public.apiBaseUrl}/suggestions/court-decisions`, {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: payload,
      })

      showSaveModal.value = false
      router.push({
        path: '/confirmation',
        query: { message: 'Thanks, we have received your submission.' },
      })
    } catch (err) {
      saveModalErrors.value = {
        general:
          'There was a problem submitting your suggestion. Please try again.',
      }
      console.error('Submission failed:', err)
    }
  })()
}

async function onSubmit() {
  const res = await $fetch('/api/submit', {
    method: 'POST',
    body: { token /* form fields */ },
  })
  if (res.success) {
    // handle success
  } else {
    // handle error
  }
  turnstile.value?.reset()
}
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
