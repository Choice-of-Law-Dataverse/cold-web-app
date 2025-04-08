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
                    processedAnswerData?.['Domestic Legal Provisions'] ||
                    processedAnswerData?.['Jurisdictions Literature ID']
                      ? [
                          value ||
                            processedAnswerData?.[
                              'Domestic Legal Provisions'
                            ] ||
                            processedAnswerData?.[
                              'Jurisdictions Literature ID'
                            ],
                        ]
                      : []),
                  ].filter(Boolean)
                "
                :fallbackData="processedAnswerData"
                :valueClassMap="valueClassMap"
                :noLinkList="[
                  processedAnswerData?.['Jurisdictions Literature ID'],
                ]"
                :fetchOupChapter="true"
                :fetchPrimarySource="true"
              />
            </section>
          </template>

          <!-- Custom rendering for Court Decisions ID -->
          <template #court-decisions-id="{ value }">
            <section>
              <span class="label">related cases</span>
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
import { onMounted } from 'vue'
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
