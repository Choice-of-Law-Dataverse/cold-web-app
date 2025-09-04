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
        </template>
        <UInput
          v-model="caseCitation"
          class="mt-2"
          placeholder="e.g., Doe v. Smith, 123 A.3d 456"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.case_title">
        <template #label>
          <span class="label">Case title (optional)</span>
        </template>
        <UInput v-model="caseTitle" class="mt-2" placeholder="Case title" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.official_source_url">
        <template #label>
          <span class="label">Official source link</span>
        </template>
        <UInput
          v-model="officialSourceUrl"
          class="mt-2"
          placeholder="https://…"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Publication date</span>
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

      <UFormGroup size="lg" class="mt-8" :error="errors.copyright_issues">
        <template #label>
          <span class="label">Copyright issues</span>
        </template>
        <UInput
          v-model="copyrightIssues"
          class="mt-2"
          placeholder="e.g., none / unknown / describe restrictions"
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
import { ref, watch } from 'vue'
import { useHead, useRouter } from '#imports'
import { z } from 'zod'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import DatePicker from '@/components/ui/DatePicker.vue'
import CancelModal from '@/components/ui/CancelModal.vue'
import SaveModal from '@/components/ui/SaveModal.vue'
import { format } from 'date-fns'

const config = useRuntimeConfig()

// Form data
const caseCitation = ref('')
const caseTitle = ref('')
const officialSourceUrl = ref('')
const copyrightIssues = ref('')
const datePublication = ref(new Date())

// Required by SaveModal (kept for parity with other pages)
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

// Ensure Submit button reactivity when token changes
watch(token, () => {})

// Validation schema
const formSchema = z.object({
  case_citation: z
    .string()
    .min(1, { message: 'Case citation is required' })
    .min(3, { message: 'Case citation must be at least 3 characters long' }),
  official_source_url: z
    .string()
    .url({
      message: 'Link must be a valid URL. It must start with "https://"',
    }),
  copyright_issues: z
    .string()
    .min(1, {
      message:
        'Please specify copyright issues (e.g., none/unknown or describe)',
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
