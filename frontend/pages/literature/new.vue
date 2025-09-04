<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="Literature"
    :hideBackButton="true"
    headerMode="new"
    @open-save-modal="openSaveModal"
    @open-cancel-modal="showCancelModal = true"
    :showNotificationBanner="true"
    :notificationBannerMessage="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
  >
    <div class="section-gap p-0 m-0">
      <UFormGroup size="lg" :error="errors.author">
        <template #label>
          <span class="label">Author</span>
        </template>
        <UInput v-model="author" class="mt-2" placeholder="Author(s)" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.title">
        <template #label>
          <span class="label">Title</span>
        </template>
        <UInput v-model="title" class="mt-2" placeholder="Work title" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.publication_title">
        <template #label>
          <span class="label">Publication title</span>
        </template>
        <UInput
          v-model="publicationTitle"
          class="mt-2"
          placeholder="Journal / Book / Proceedings"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.publication_year">
        <template #label>
          <span class="label">Publication year</span>
        </template>
        <UInput
          v-model="publicationYear"
          class="mt-2"
          placeholder="e.g., 2024"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.url">
        <template #label>
          <span class="label">URL</span>
        </template>
        <UInput v-model="url" class="mt-2" placeholder="https://…" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8" :error="errors.doi">
        <template #label>
          <span class="label">DOI</span>
        </template>
        <UInput v-model="doi" class="mt-2" placeholder="e.g., 10.1000/xyz123" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Publication date</span>
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="format(publicationDate, 'dd MMMM yyyy')"
            class="mt-2"
          />
          <template #panel="{ close }">
            <DatePicker v-model="publicationDate" @close="close" />
          </template>
        </UPopover>
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">ISBN</span>
        </template>
        <UInput v-model="isbn" class="mt-2" placeholder="ISBN" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">ISSN</span>
        </template>
        <UInput v-model="issn" class="mt-2" placeholder="ISSN" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Jurisdiction</span>
        </template>
        <UInput
          v-model="jurisdiction"
          class="mt-2"
          placeholder="Jurisdiction"
        />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Theme</span>
        </template>
        <UInput v-model="theme" class="mt-2" placeholder="Theme" />
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
    :date="publicationDate"
    :pdfFile="pdfFile"
    :link="url"
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

// Form fields (all optional)
const author = ref('')
const title = ref('')
const publicationTitle = ref('')
const publicationYear = ref('')
const url = ref('')
const doi = ref('')
const publicationDate = ref(new Date())
const isbn = ref('')
const issn = ref('')
const jurisdiction = ref('')
const theme = ref('')

// For SaveModal parity
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

watch(token, () => {})

// Validation (only validate formats if provided)
const formSchema = z.object({
  url: z
    .string()
    .url({ message: 'URL must be valid and start with "https://"' })
    .optional()
    .or(z.literal('')),
  publication_year: z
    .string()
    .regex(/^\d{4}$/u, { message: 'Year must be 4 digits (e.g., 2024)' })
    .optional()
    .or(z.literal('')),
  doi: z.string().optional().or(z.literal('')),
})

const errors = ref({})
const saveModalErrors = ref({})

const router = useRouter()
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New Literature — CoLD' })

function validateForm() {
  try {
    const formData = {
      url: url.value,
      publication_year: publicationYear.value,
      doi: doi.value,
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
    author: author.value || undefined,
    title: title.value || undefined,
    publication_title: publicationTitle.value || undefined,
    publication_year:
      (publicationYear.value && Number(publicationYear.value)) || undefined,
    url: url.value || undefined,
    doi: doi.value || undefined,
    publication_date: format(publicationDate.value, 'yyyy-MM-dd'),
    isbn: isbn.value || undefined,
    issn: issn.value || undefined,
    jurisdiction: jurisdiction.value || undefined,
    theme: theme.value || undefined,
    // Submitter metadata from SaveModal
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
  }

  console.log('Submitting:', JSON.stringify(payload, null, 2))
  ;(async () => {
    try {
      await $fetch(`${config.public.apiBaseUrl}/suggestions/literature`, {
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
