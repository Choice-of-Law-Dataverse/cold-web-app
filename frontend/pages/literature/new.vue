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
      <!-- Jurisdiction (optional) -->
      <UFormGroup size="lg">
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

      <!-- Year (required) -->
      <UFormGroup
        size="lg"
        class="mt-8"
        hint="Required"
        :error="errors.publication_year"
      >
        <template #label>
          <span class="label">Year</span>
        </template>
        <UInput v-model="publicationYear" class="mt-2" />
      </UFormGroup>

      <!-- Author(s) (required) -->
      <UFormGroup size="lg" class="mt-8" hint="Required" :error="errors.author">
        <template #label>
          <span class="label">Author</span>
        </template>
        <UInput v-model="author" class="mt-2" />
      </UFormGroup>

      <!-- Title (required) -->
      <UFormGroup size="lg" class="mt-8" hint="Required" :error="errors.title">
        <template #label>
          <span class="label">Title</span>
        </template>
        <UInput v-model="title" class="mt-2" />
      </UFormGroup>

      <!-- Publication (optional) -->
      <UFormGroup size="lg" class="mt-8" :error="errors.publication_title">
        <template #label>
          <span class="label">Publication title</span>
        </template>
        <UInput v-model="publicationTitle" class="mt-2" />
      </UFormGroup>

      <!-- URL (optional) -->
      <UFormGroup size="lg" class="mt-8" :error="errors.url">
        <template #label>
          <span class="label">URL</span>
        </template>
        <UInput v-model="url" class="mt-2" />
      </UFormGroup>

      <!-- DOI (optional) -->
      <UFormGroup size="lg" class="mt-8" :error="errors.doi">
        <template #label>
          <span class="label">DOI</span>
        </template>
        <UInput v-model="doi" class="mt-2" />
      </UFormGroup>

      <!-- Date (optional) -->
      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Publication date</span>
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="
              publicationDate
                ? format(publicationDate, 'dd MMMM yyyy')
                : 'Add date'
            "
            class="mt-2"
          />
          <template #panel="{ close }">
            <DatePicker v-model="publicationDate" @close="close" />
          </template>
        </UPopover>
      </UFormGroup>

      <!-- ISBN (optional) -->
      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">ISBN</span>
        </template>
        <UInput v-model="isbn" class="mt-2" />
      </UFormGroup>

      <!-- ISSN (optional) -->
      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">ISSN</span>
        </template>
        <UInput v-model="issn" class="mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Theme</span>
        </template>
        <UInput v-model="theme" class="mt-2" />
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
    :date="publicationDate || null"
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
import { ref, watch, onMounted } from 'vue'
import { useHead, useRouter } from '#imports'
import { z } from 'zod'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import DatePicker from '@/components/ui/DatePicker.vue'
import CancelModal from '@/components/ui/CancelModal.vue'
import SaveModal from '@/components/ui/SaveModal.vue'
import SearchFilters from '@/components/search-results/SearchFilters.vue'
import { format } from 'date-fns'

const config = useRuntimeConfig()

// Form fields
const author = ref('')
const title = ref('')
const publicationTitle = ref('')
const publicationYear = ref('')
const url = ref('')
const doi = ref('')
const publicationDate = ref(null)
const isbn = ref('')
const issn = ref('')
const theme = ref('')

// Jurisdiction selector
const selectedJurisdiction = ref([])
const jurisdictionOptions = ref([{ label: 'All Jurisdictions' }])

// For SaveModal parity
const specialists = ref([''])
const pdfFile = ref(null)
const email = ref('')
const comments = ref('')

const turnstile = ref()
const token = ref('')

watch(token, () => {})

// Load jurisdictions similar to other pages
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

// Validation (required fields only)
const formSchema = z.object({
  author: z
    .string()
    .min(1, { message: 'Author is required' })
    .min(3, { message: 'Author must be at least 3 characters long' }),
  title: z
    .string()
    .min(1, { message: 'Title is required' })
    .min(3, { message: 'Title must be at least 3 characters long' }),
  publication_year: z
    .string()
    .regex(/^\d{4}$/u, { message: 'Year must be 4 digits (e.g., 2024)' }),
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
      author: author.value,
      title: title.value,
      publication_year: publicationYear.value,
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
    author: author.value,
    title: title.value,
    publication_title: publicationTitle.value || undefined,
    publication_year: Number(publicationYear.value),
    url: url.value || undefined,
    doi: doi.value || undefined,
    publication_date:
      publicationDate && publicationDate.value
        ? format(publicationDate.value, 'yyyy-MM-dd')
        : undefined,
    isbn: isbn.value || undefined,
    issn: issn.value || undefined,
    jurisdiction:
      (Array.isArray(selectedJurisdiction.value) &&
        selectedJurisdiction.value[0]?.label) ||
      undefined,
    theme: theme.value || undefined,
    // Submitter metadata from SaveModal
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
  }

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
