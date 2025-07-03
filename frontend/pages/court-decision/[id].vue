<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="modifiedCourtDecision"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Court Decisions"
  >
    <!-- Slot for Domestic Legal Provisions -->
    <template #domestic-legal-provisions="{ value }">
      <div :class="valueClassMap['Domestic Legal Provisions']">
        <ProvisionRenderer
          v-if="value"
          :id="value"
          section="Domestic Legal Provisions"
          :sectionLabel="
            courtDecisionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions'
            )?.label
          "
          :sectionTooltip="
            courtDecisionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions'
            )?.tooltip
          "
          table="Domestic Instruments"
          class="mb-8"
        />
      </div>
    </template>
    <!-- Custom rendering for Quote section -->
    <template #quote>
      <section class="section-gap p-0 m-0">
        <div
          v-if="
            modifiedCourtDecision &&
            (modifiedCourtDecision['Quote'] ||
              modifiedCourtDecision['Translated Excerpt'])
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <span class="label">Quote</span>
              <InfoTooltip
                v-if="
                  computedKeyLabelPairs.find((pair) => pair.key === 'Quote')
                    ?.tooltip
                "
                :text="
                  computedKeyLabelPairs.find((pair) => pair.key === 'Quote')
                    ?.tooltip
                "
                class="ml-[-8px]"
              />
            </div>
            <div
              v-if="
                hasEnglishQuoteTranslation &&
                modifiedCourtDecision['Quote'] &&
                modifiedCourtDecision['Quote'].trim() !== ''
              "
              class="flex items-center gap-1"
            >
              <span
                class="label-key-provision-toggle mr-[-0px]"
                :class="{
                  'opacity-25': showEnglishQuote,
                  'opacity-100': !showEnglishQuote,
                }"
              >
                Original
              </span>
              <UToggle
                v-model="showEnglishQuote"
                size="2xs"
                class="bg-[var(--color-cold-gray)]"
              />
              <span
                class="label-key-provision-toggle"
                :class="{
                  'opacity-25': !showEnglishQuote,
                  'opacity-100': showEnglishQuote,
                }"
              >
                English
              </span>
            </div>
          </div>
          <div>
            <span style="white-space: pre-line">
              {{
                showEnglishQuote &&
                hasEnglishQuoteTranslation &&
                modifiedCourtDecision['Quote'] &&
                modifiedCourtDecision['Quote'].trim() !== ''
                  ? modifiedCourtDecision['Translated Excerpt']
                  : modifiedCourtDecision['Quote'] ||
                    modifiedCourtDecision['Translated Excerpt']
              }}
            </span>
          </div>
        </div>
      </section>
    </template>
    <!-- Custom rendering for Related Questions section -->
    <template #related-questions>
      <section class="section-gap p-0 m-0">
        <RelatedQuestions
          :jurisdictionCode="
            modifiedCourtDecision['Jurisdictions Alpha-3 Code'] || ''
          "
          :questions="modifiedCourtDecision['Questions'] || ''"
          :tooltip="
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Related Questions'
            )?.tooltip
          "
        />
      </section>
    </template>
    <template #related-literature>
      <section class="section-gap p-0 m-0">
        <RelatedLiterature
          :themes="themes"
          :valueClassMap="valueClassMap['Related Literature']"
          :useId="false"
          :tooltip="
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.tooltip
          "
        />
      </section>
    </template>

    <!-- Custom rendering for Full Text (Original Text) section -->
<template #['original-text']="{ value }">
  <section v-if="value && value.trim() !== ''" class="section-gap p-0 m-0">
    <div class="flex items-center mb-2 mt-12">
      <span class="label">
        {{
          computedKeyLabelPairs.find((pair) => pair.key === 'Original Text')?.label || 'Full Text'
        }}
      </span>
    </div>
    <div :class="valueClassMap['Original Text']">
      <span v-if="!showFullText && value.length > 400">
        {{ value.slice(0, 400) }}<span v-if="value.length > 400">…</span>
        <div>
          <NuxtLink class="ml-2 cursor-pointer" @click="showFullText = true">
            <Icon name="material-symbols:add" :class="iconClass" />
            Show entire full text
          </NuxtLink>
        </div>
      </span>
      <span v-else>
        {{ value }}
        <div>
          <NuxtLink v-if="value.length > 400" class="ml-2 cursor-pointer" @click="showFullText = false">
            <Icon name="material-symbols:remove" :class="iconClass" />
            Show less
          </NuxtLink>
        </div>
      </span>
      <div>
        <a
          class="ml-2"
          :href="downloadPDFLink"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Icon name="i-material-symbols:arrow-circle-down-outline" :class="iconClass" />
          <span class="ml-1">Download the case as a PDF</span>
        </a>
      </div>
    </div>
  </section>
</template>
  </BaseDetailLayout>

  <!-- Error Alert -->
  <UAlert
    v-if="error"
    type="error"
    class="mx-auto mt-4"
    style="max-width: var(--container-width)"
  >
    {{ error }}
  </UAlert>
</template>

<script setup>
import { computed, onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import RelatedLiterature from '@/components/literature/RelatedLiterature.vue'
import RelatedQuestions from '@/components/legal/RelatedQuestions.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import ProvisionRenderer from '@/components/legal/SectionRenderer.vue'
import { useApiFetch } from '@/composables/useApiFetch'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { courtDecisionConfig } from '@/config/pageConfigs'
import { formatDate } from '@/utils/format.js'
import { useHead } from '#imports'

defineProps({
  iconClass: {
    type: String,
    default: 'text-base translate-y-[3px] mt-2 ml-[-12px]',
  },
})

const route = useRoute()
const router = useRouter()
const { loading, error, data: courtDecision, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig
)

const themes = computed(() => {
  if (!courtDecision.value) return ''
  const themesData = courtDecision.value['Themes']
  return themesData || ''
})

const modifiedCourtDecision = computed(() => {
  if (!courtDecision.value) return null
  return {
    ...courtDecision.value,
    'Case Title':
      courtDecision.value['Case Title'] === 'Not found'
        ? courtDecision.value['Case Citation']
        : courtDecision.value['Case Title'],
    'Related Literature': themes.value,
    'Case Citation': courtDecision.value['Case Citation'],
    Questions: courtDecision.value['Questions'],
    'Jurisdictions Alpha-3 Code':
      courtDecision.value['Jurisdictions Alpha-3 Code'],
    'Publication Date ISO': formatDate(
      courtDecision.value['Publication Date ISO']
    ),
    'Date of Judgment': formatDate(courtDecision.value['Date of Judgment']),
  }
})

const showEnglishQuote = ref(true)
const hasEnglishQuoteTranslation = computed(() => {
  return !!(
    modifiedCourtDecision.value &&
    modifiedCourtDecision.value['Translated Excerpt'] &&
    modifiedCourtDecision.value['Translated Excerpt'].trim() !== ''
  )
})

// For Full Text show more/less
const showFullText = ref(false)

// PDF download link logic (same as BaseCardHeader.vue)
const downloadPDFLink = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  const contentType = segments[0] || 'unknown'
  const id = segments[1] || ''
  const folder = `${contentType}s`
  return `https://choiceoflawdataverse.blob.core.windows.net/${folder}/${id}.pdf`
})

const fetchCourtDecision = async () => {
  try {
    await fetchData({
      table: 'Court Decisions',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `Court decision not found` },
      })
    } else {
      console.error('Failed to fetch court decision:', err)
    }
  }
}

onMounted(() => {
  fetchCourtDecision()
})

// Refetch if the route ID changes
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchCourtDecision()
    }
  }
)

// Set dynamic page title based on Case Title or Citation
watch(
  modifiedCourtDecision,
  (newVal) => {
    if (!newVal) return
    const caseTitle = newVal['Case Title']
    const citation = newVal['Case Citation']
    const pageTitle =
      caseTitle && caseTitle.trim() && caseTitle !== 'Not found'
        ? `${caseTitle} — CoLD`
        : citation && citation.trim()
          ? `${citation} — CoLD`
          : 'Court Decision — CoLD'
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
  },
  { immediate: true }
)
</script>
