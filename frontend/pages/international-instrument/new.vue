<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="International Instrument"
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
      <UFormGroup size="lg" hint="Required" :error="errors.name">
        <template #label>
          <span class="label">Title</span>
        </template>
        <UInput v-model="name" class="mt-2 cold-input" />
      </UFormGroup>
      <UFormGroup size="lg" class="mt-8">
        <!-- <template #label>
          <span class="label">Specialists</span>
          <InfoTooltip :text="tooltipInternationalInstrumentSpecialist" />
        </template>
        <div
          v-for="(specialist, idx) in specialists"
          :key="idx"
          class="flex items-center mt-2"
        >
          <UInput
            v-model="specialists[idx]"
            placeholder="Specialist’s name"
            class="flex-1"
          />
          <UButton
            v-if="idx > 0"
            icon="i-heroicons-x-mark"
            color="red"
            variant="ghost"
            class="ml-2"
            @click="removeSpecialist(idx)"
            aria-label="Remove specialist"
          />
        </div>
        <template v-for="(specialist, idx) in specialists">
          <div
            v-if="specialists[idx] && idx === specialists.length - 1"
            :key="'add-btn-' + idx"
          >
            <UButton
              class="mt-2"
              color="primary"
              variant="soft"
              icon="i-heroicons-plus"
              @click="addSpecialist"
              >Add another specialist</UButton
            >
          </div> 
        </template> -->
      </UFormGroup>
      <!-- <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">PDF</span>
          <InfoTooltip :text="tooltipInternationalInstrumentSpecialist" />
        </template>
        <UInput
          type="file"
          icon="i-material-symbols:upload-file"
          @change="onPdfChange"
        />
      </UFormGroup> -->
      <UFormGroup size="lg" class="mt-8" hint="Required" :error="errors.link">
        <template #label>
          <span class="label">Link</span>
          <InfoTooltip :text="tooltipInternationalInstrumentLink" />
        </template>
        <UInput
          v-model="link"
          class="mt-2 cold-input"
          placeholder="https://…"
        />
      </UFormGroup>
      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.instrument_date"
      >
        <template #label>
          <span class="label">Date</span>
          <InfoTooltip :text="tooltipInternationalInstrumentDate" />
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
            class="mt-2 cold-date-trigger"
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
    :name="name"
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
import tooltipInternationalInstrumentSpecialist from '@/content/info_boxes/international_instrument/specialists.md?raw'
import tooltipInternationalInstrumentDate from '@/content/info_boxes/international_instrument/date.md?raw'
import tooltipInternationalInstrumentLink from '@/content/info_boxes/international_instrument/link.md?raw'

import { format } from 'date-fns'
const date = ref(new Date())

const config = useRuntimeConfig()

// Form data
const name = ref('')
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
  name: z
    .string()
    .min(1, { message: 'Title is required' })
    .min(3, { message: 'Title must be at least 3 characters long' }),
  link: z
    .string()
    .min(1, { message: 'URL is required' })
    .url({ message: 'URL must be valid and start with "https://"' }),
  instrument_date: z.date({ required_error: 'Date is required' }),
})

// Form validation state
const errors = ref({})
const saveModalErrors = ref({})

const router = useRouter()
const emit = defineEmits(['close-cancel-modal', 'close-save-modal'])
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New International Instrument — CoLD' })

function validateForm() {
  try {
    const formData = {
      name: name.value,
      link: link.value,
      instrument_date: date.value,
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
    name: name.value,
    url: link.value,
    attachment: '', // ignored for now
    instrument_date:
      date && date.value ? format(date.value, 'yyyy-MM-dd') : undefined,
    // Submitter metadata from SaveModal
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
  }

  // Explicitly log the exact payload we send
  ;(async () => {
    try {
      await $fetch(
        `/api/proxy/suggestions/international-instruments`,
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
