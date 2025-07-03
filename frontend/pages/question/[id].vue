<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedAnswerData"
    :keyLabelPairs="filteredKeyLabelPairs"
    :valueClassMap="valueClassMap"
    :sourceTable="'Question'"
  >
    <!-- Custom rendering for Legal provision articles -->
    <template #domestic-legal-provisions="{ value }">
      <section class="section-gap">
        <span class="label">
          {{
            filteredKeyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions'
            )?.label || 'Source fallback'
          }}
          <InfoTooltip
            v-if="
              filteredKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
            :text="
              filteredKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
          />
        </span>
        <QuestionSourceList
          :sources="
            [
              ...(value || processedAnswerData?.['Domestic Legal Provisions']
                ? [value || processedAnswerData?.['Domestic Legal Provisions']]
                : []),
            ].filter(Boolean)
          "
          :fallbackData="processedAnswerData"
          :valueClassMap="valueClassMap"
          :fetchOupChapter="true"
          :fetchPrimarySource="true"
        />
      </section>
    </template>

    <!-- Custom rendering for Court Decisions ID -->
    <template #court-decisions-id="{ value }">
      <section id="related-court-decisions" class="section-gap">
        <span class="label">
          {{
            filteredKeyLabelPairs.find(
              (pair) => pair.key === 'Court Decisions ID'
            )?.label || 'Related Court Decisions'
          }}
          <InfoTooltip
            v-if="
              filteredKeyLabelPairs.find(
                (pair) => pair.key === 'Court Decisions ID'
              )?.tooltip
            "
            :text="
              filteredKeyLabelPairs.find(
                (pair) => pair.key === 'Court Decisions ID'
              )?.tooltip
            "
          />
        </span>
        <CourtDecisionRenderer
          :value="value"
          :valueClassMap="valueClassMap['Court Decisions ID']"
          :emptyValueBehavior="
            filteredKeyLabelPairs.find(
              (pair) => pair.key === 'Court Decisions ID'
            )?.emptyValueBehavior
          "
        />
      </section>
    </template>

    <template #related-literature>
      <section class="section-gap">
        <RelatedLiterature
          :themes="processedAnswerData?.Themes"
          :literatureId="processedAnswerData?.['Jurisdictions Literature ID']"
          :mode="'both'"
          :valueClassMap="valueClassMap['Related Literature']"
          :label="
            filteredKeyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.label || 'Related Literature'
          "
          :emptyValueBehavior="
            questionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.emptyValueBehavior
          "
          :tooltip="
            filteredKeyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.tooltip
          "
        />
      </section>
    </template>
  </BaseDetailLayout>
  <CountryReportLink :processedAnswerData="processedAnswerData" />
</template>

<script setup>
import { onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import CourtDecisionRenderer from '@/components/legal/CourtDecisionRenderer.vue'
import RelatedLiterature from '@/components/literature/RelatedLiterature.vue'
import QuestionSourceList from '@/components/sources/QuestionSourceList.vue'
import CountryReportLink from '@/components/ui/CountryReportLink.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import { useQuestion } from '@/composables/useQuestion'
import { questionConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()
const {
  loading,
  processedAnswerData,
  filteredKeyLabelPairs,
  valueClassMap,
  fetchAnswer,
} = useQuestion()

onMounted(async () => {
  try {
    const id = route.params.id
    await fetchAnswer(id)
    // Wait for the DOM to update then scroll if the hash is present
    await nextTick()
    if (window.location.hash === '#related-court-decisions') {
      const target = document.getElementById('related-court-decisions')
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' })
      }
    }
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `${err.table} not found` },
      })
    } else {
      console.error('Error fetching question:', err)
    }
  }
})

// Set dynamic page title: 'Jurisdictions: Question — CoLD'
watch(
  processedAnswerData,
  (newVal) => {
    if (!newVal) return
    const question = newVal['Question'] || ''
    const jurisdictions = newVal['Jurisdictions'] || ''
    let pageTitle = 'CoLD'
    if (question && jurisdictions) {
      pageTitle = `${jurisdictions}: ${question} — CoLD`
    } else if (question) {
      pageTitle = `${question} — CoLD`
    } else if (jurisdictions) {
      pageTitle = `${jurisdictions} — CoLD`
    }
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
