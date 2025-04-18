<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="processedAnswerData"
          :keyLabelPairs="filteredKeyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Question"
        >
          <!-- Custom rendering for Legal provision articles -->
          <template #domestic-legal-provisions="{ value }">
            <section>
              <span class="label">Source</span>
              <QuestionSourceList
                :sources="
                  [
                    ...(value ||
                    processedAnswerData?.['Domestic Legal Provisions']
                      ? [
                          value ||
                            processedAnswerData?.['Domestic Legal Provisions'],
                        ]
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
            <section id="related-court-decisions">
              <span class="label">Related Court Decisions</span>
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

          <!-- Related Literature -->
          <template #related-literature>
            <RelatedLiterature
              :themes="processedAnswerData?.Themes || ''"
              :valueClassMap="valueClassMap['Related Literature']"
            />
          </template>
        </DetailDisplay>

        <!-- Error State -->
        <div v-if="error" class="text-red-500 mt-4">
          {{ error }}
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetailDisplay from '~/components/ui/BaseDetailDisplay.vue'
import CourtDecisionRenderer from '~/components/legal/CourtDecisionRenderer.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import QuestionSourceList from '~/components/sources/QuestionSourceList.vue'
import { useQuestion } from '~/composables/useQuestion'

const route = useRoute()
const router = useRouter()
const {
  loading,
  error,
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
</script>

<style>
/* Harmonized spacing for all .label elements */
/* .label {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
} */

/* Adjust section spacing to match label spacing */
/* #related-court-decisions {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-top: 0;
  padding-bottom: 0;
} */
</style>
