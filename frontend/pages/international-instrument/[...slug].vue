<template>
  <div v-if="isEditPage">
    <BaseDetailLayout
      :loading="loading"
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
      <div class="section-gap p-0 m-0">
        <UFormGroup size="lg" hint="Required" :error="errors.name">
          <template #label>
            <span class="label">Name</span>
          </template>
          <UInput
            v-model="name"
            class="mt-2"
            placeholder="Name of the International Instrument"
          />
        </UFormGroup>
        <UFormGroup size="lg" class="mt-8">
          <template #label>
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
          </template>
        </UFormGroup>
        <UFormGroup size="lg" class="mt-8">
          <template #label>
            <span class="label">PDF</span>
            <InfoTooltip :text="tooltipInternationalInstrumentSpecialist" />
          </template>
          <UInput
            type="file"
            icon="i-material-symbols:upload-file"
            @change="onPdfChange"
          />
          <div v-if="pdfFileName" class="mt-2 text-sm text-gray-500">
            Current: {{ pdfFileName }}
          </div>
        </UFormGroup>
        <UFormGroup size="lg" class="mt-8" :error="errors.link">
          <template #label>
            <span class="label">Link</span>
            <InfoTooltip :text="tooltipInternationalInstrumentLink" />
          </template>
          <UInput v-model="link" class="mt-2" placeholder="Link" />
        </UFormGroup>
        <UFormGroup size="lg" class="mt-8">
          <template #label>
            <span class="label">Date</span>
            <InfoTooltip :text="tooltipInternationalInstrumentDate" />
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
      :name="name"
      :specialists="specialists"
      :date="date"
      :pdfFile="pdfFile"
      :link="link"
      :instrumentId="instrumentApiId"
      @update:email="(val) => (email = val)"
      @update:comments="(val) => (comments = val)"
      @update:token="(val) => (token = val)"
      @update:saveModalErrors="(val) => (saveModalErrors.value = val)"
      @save="handleEditSave"
    />
  </div>
  <div v-else>Page not found</div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { z } from 'zod'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import DatePicker from '@/components/ui/DatePicker.vue'
import CancelModal from '@/components/ui/CancelModal.vue'
import SaveModal from '@/components/ui/SaveModal.vue'
import tooltipInternationalInstrumentSpecialist from '@/content/info_boxes/international_instrument/specialists.md?raw'
import tooltipInternationalInstrumentDate from '@/content/info_boxes/international_instrument/date.md?raw'
import tooltipInternationalInstrumentLink from '@/content/info_boxes/international_instrument/link.md?raw'
import { format, parseISO } from 'date-fns'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()
const isEditPage = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) && slug.length === 2 && slug[1] === 'edit'
})
const instrumentId = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) ? slug[0] : null
})

const loading = ref(true)
const name = ref('')
const link = ref('')
const specialists = ref([''])
const pdfFile = ref(null)
const pdfFileName = ref('')
const date = ref(new Date())
const email = ref('')
const comments = ref('')
const token = ref('')
const turnstile = ref()
const errors = ref({})
const saveModalErrors = ref({})
const showSaveModal = ref(false)
const showCancelModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'
const instrumentApiId = ref(null)

const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: 'Name is required' })
    .min(3, { message: 'Name must be at least 3 characters long' }),
  specialists: z.array(z.string()).optional(),
  link: z
    .string()
    .url({ message: 'Link must be a valid URL. It must start with "https://"' })
    .optional()
    .or(z.literal('')),
})

function validateForm() {
  try {
    const formData = {
      name: name.value,
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
  let file = null
  if (event instanceof FileList) {
    file = event[0] || null
  } else if (event && event.target && event.target.files) {
    file = event.target.files[0] || null
  } else if (event && event.files) {
    file = event.files[0] || null
  }
  pdfFile.value = file
  pdfFileName.value = file ? file.name : ''
}

function addSpecialist() {
  specialists.value.push('')
}
function removeSpecialist(idx) {
  specialists.value.splice(idx, 1)
}

function confirmCancel() {
  if (isEditPage.value && instrumentId.value) {
    router.push(`/international-instrument/${instrumentId.value}`)
  } else {
    router.push('/')
  }
}

function handleEditSave() {
  showSaveModal.value = false
  router.replace({
    path: '/confirmation',
    query: {
      message: 'Thanks, we have received your edit suggestions.',
    },
  })
}

// Fetch and prefill data
async function fetchInstrument() {
  loading.value = true
  try {
    if (!instrumentId.value) {
      loading.value = false
      return
    }
    const apiBaseUrl =
      (typeof useRuntimeConfig === 'function'
        ? useRuntimeConfig().public.apiBaseUrl
        : '') || window.location.origin
    const fastApiKey =
      typeof useRuntimeConfig === 'function'
        ? useRuntimeConfig().public.FASTAPI
        : ''
    const response = await fetch(`${apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        authorization: `Bearer ${fastApiKey}`,
      },
      body: JSON.stringify({
        table: 'International Instruments',
        id: instrumentId.value,
      }),
    })
    const responseText = await response.text()
    if (!response.ok) throw new Error('Failed to fetch instrument')
    const data = JSON.parse(responseText)
    name.value = data['Name'] || data['Title (in English)'] || ''
    specialists.value = data['Specialists']
      ? data['Specialists'].split(',').map((s) => s.trim())
      : ['']
    date.value = data['Date'] ? parseISO(data['Date']) : new Date()
    link.value = data['URL'] || ''
    pdfFileName.value = data['PDF'] || ''
    instrumentApiId.value = data['ID'] || null
  } catch (err) {
    // Optionally handle error
  } finally {
    loading.value = false
  }
}

watch(
  [isEditPage, instrumentId],
  ([edit, id]) => {
    if (edit && id) {
      fetchInstrument()
    }
  },
  { immediate: true }
)

watch(
  [isEditPage, name],
  ([edit, currentName]) => {
    if (edit) {
      const pageTitle =
        currentName && currentName.trim()
          ? `Edit ${currentName} — CoLD`
          : 'Edit International Instrument — CoLD'
      useHead({
        title: pageTitle,
        link: [
          {
            rel: 'canonical',
            href: `https://cold.global${route.fullPath}`,
          },
        ],
        meta: [
          {
            name: 'description',
            content: pageTitle,
          },
        ],
      })
    }
  },
  { immediate: true }
)
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
