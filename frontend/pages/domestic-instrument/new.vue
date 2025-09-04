<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="Domestic Instrument"
    :hideBackButton="true"
    headerMode="new"
    @open-save-modal="openSaveModal"
    @open-cancel-modal="showCancelModal = true"
    :showNotificationBanner="true"
    :notificationBannerMessage="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
  >
    <div class="section-gap p-0 m-0">
      <UFormGroup size="lg" hint="Required" :error="errors.official_title">
        <template #label>
          <span class="label">Official title</span>
        </template>
        <UInput
          v-model="officialTitle"
          class="mt-2"
          placeholder="Official title (original language)"
        />
      </UFormGroup>

      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.title_en"
      >
        <template #label>
          <span class="label">Title (English)</span>
        </template>
        <UInput v-model="titleEn" class="mt-2" placeholder="English title" />
      </UFormGroup>

      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.jurisdiction_link"
      >
        <template #label>
          <span class="label">Jurisdiction link</span>
        </template>
        <UInput
          v-model="jurisdictionLink"
          class="mt-2"
          placeholder="https://…"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" hint="Required">
        <template #label>
          <span class="label">Entry into force</span>
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="format(entryIntoForce, 'dd MMMM yyyy')"
            class="mt-2"
          />
          <template #panel="{ close }">
            <DatePicker v-model="entryIntoForce" is-required @close="close" />
          </template>
        </UPopover>
      </UFormGroup>

      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.source_url"
      >
        <template #label>
          <span class="label">Source link</span>
        </template>
        <UInput v-model="sourceUrl" class="mt-2" placeholder="https://…" />
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
    :name="titleEn"
    :specialists="specialists"
    :date="entryIntoForce"
    :pdfFile="pdfFile"
    :link="sourceUrl"
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
const officialTitle = ref('')
const titleEn = ref('')
const jurisdictionLink = ref('')
const entryIntoForce = ref(new Date())
const sourceUrl = ref('')

// For SaveModal parity
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

watch(token, () => {})

// Validation schema
const formSchema = z.object({
  official_title: z
    .string()
    .min(1, { message: 'Official title is required' })
    .min(3, { message: 'Official title must be at least 3 characters long' }),
  title_en: z
    .string()
    .min(1, { message: 'English title is required' })
    .min(3, { message: 'English title must be at least 3 characters long' }),
  jurisdiction_link: z.string().url({
    message: 'Jurisdiction link must be a valid URL starting with "https://"',
  }),
  source_url: z.string().url({
    message: 'Source link must be a valid URL starting with "https://"',
  }),
})

// State
const errors = ref({})
const saveModalErrors = ref({})

const router = useRouter()
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New Domestic Instrument — CoLD' })

function validateForm() {
  try {
    const formData = {
      official_title: officialTitle.value,
      title_en: titleEn.value,
      jurisdiction_link: jurisdictionLink.value,
      source_url: sourceUrl.value,
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
    jurisdiction_link: jurisdictionLink.value,
    official_title: officialTitle.value,
    title_en: titleEn.value,
    entry_into_force: format(entryIntoForce.value, 'yyyy-MM-dd'),
    source_url: sourceUrl.value,
    // Submitter metadata from SaveModal
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
  }

  console.log('Submitting:', JSON.stringify(payload, null, 2))
  ;(async () => {
    try {
      await $fetch(
        `${config.public.apiBaseUrl}/suggestions/domestic-instruments`,
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
