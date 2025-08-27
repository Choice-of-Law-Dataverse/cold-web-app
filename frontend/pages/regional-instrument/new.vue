<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="Regional Instrument"
    :hideBackButton="true"
    headerMode="new"
    @open-save-modal="openSaveModal"
    @open-cancel-modal="showCancelModal = true"
    :showNotificationBanner="true"
    :notificationBannerMessage="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
  >
    <!-- Always render this section, even if keyLabelPairs is empty -->
    <div class="section-gap p-0 m-0">
      <UFormGroup size="lg" :error="errors.abbreviation">
        <template #label>
          <span class="label">Abbreviation</span>
        </template>
        <UInput
          v-model="abbreviation"
          class="mt-2"
          placeholder="Abbreviation of the Regional Instrument"
        />
      </UFormGroup>
      <UFormGroup size="lg" hint="Required" :error="errors.title" class="mt-8">
        <template #label>
          <span class="label">Title</span>
        </template>
        <UInput
          v-model="title"
          class="mt-2"
          placeholder="Name of the Regional Instrument"
        />
      </UFormGroup>
      <UFormGroup size="lg" class="mt-8" :error="errors.link">
        <template #label>
          <span class="label">Link</span>
        </template>
        <UInput v-model="link" class="mt-2" placeholder="Link" />
      </UFormGroup>
      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Date</span>
          <InfoTooltip :text="tooltipRegionalInstrumentDate" />
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="format(date, 'dd MMMM yyyy')"
            class="mt-2"
          />

          <template #panel="{ close }">
            <DatePicker v-model="date" is-required @close="close" />
          </template>
        </UPopover>
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
    :name="title"
    :specialists="specialists"
    :date="date"
    :pdfFile="pdfFile"
    :link="link"
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
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import DatePicker from '@/components/ui/DatePicker.vue'
import CancelModal from '@/components/ui/CancelModal.vue'
import SaveModal from '@/components/ui/SaveModal.vue'
import tooltipRegionalInstrumentDate from '@/content/info_boxes/regional_instrument/date.md?raw'

import { format } from 'date-fns'
const date = ref(new Date())

const config = useRuntimeConfig()

// Form data
const abbreviation = ref('')
const title = ref('')
const link = ref('')
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

// Ensure Submit button reactivity when token changes
watch(token, () => {
  // This will trigger reactivity for the Submit button
})

// Validation schema
const formSchema = z.object({
  title: z
    .string()
    .min(1, { message: 'Title is required' })
    .min(3, { message: 'Title must be at least 3 characters long' }),
  specialists: z.array(z.string()).optional(),
  link: z
    .string()
    .url({ message: 'Link must be a valid URL. It must start with "https://"' })
    .optional()
    .or(z.literal('')),
})

// Form validation state
const errors = ref({})
const saveModalErrors = ref({})

const router = useRouter()
const emit = defineEmits(['close-cancel-modal', 'close-save-modal'])
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New Regional Instrument — CoLD' })

function validateForm() {
  try {
    const formData = {
      title: title.value,
      specialists: specialists.value,
      link: link.value,
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

function onPdfChange(event) {
  // Handle different event types - UInput might pass FileList directly or as event.target.files
  let file = null
  if (event instanceof FileList) {
    file = event[0] || null
  } else if (event && event.target && event.target.files) {
    file = event.target.files[0] || null
  } else if (event && event.files) {
    file = event.files[0] || null
  }
  pdfFile.value = file
}

function confirmCancel() {
  router.push('/')
}

function addSpecialist() {
  specialists.value.push('')
}
function removeSpecialist(idx) {
  specialists.value.splice(idx, 1)
}

function handleNewSave() {
  const payload = {
    abbreviation: abbreviation.value, // abbreviation
    title: title.value, // title
    url: link.value, // Link
    attachment: '', // ignored for now
    instrument_date: format(date.value, 'yyyy-MM-dd'), // Date
  }

  // Explicitly log the exact payload we send
  console.log('Submitting:', JSON.stringify(payload, null, 2))
  ;(async () => {
    try {
      await $fetch(
        `${config.public.apiBaseUrl}/suggestions/regional-instruments`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: payload,
        }
      )

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
