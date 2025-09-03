<template>
  <BaseDetailLayout
    :loading="isLoading.value"
    :resultData="jurisdictionData"
    :keyLabelPairs="keyLabelPairsWithoutLegalFamily"
    :valueClassMap="valueClassMap"
    :formattedJurisdiction="[jurisdictionData?.Name]"
    sourceTable="Jurisdiction"
  >
    <template #related-literature>
      <section class="section-gap p-0 m-0">
        <RelatedLiterature
          :literature-id="jurisdictionData?.Literature"
          :valueClassMap="valueClassMap['Related Literature']"
          :useId="true"
          :label="
            keyLabelPairs.find((pair) => pair.key === 'Related Literature')
              ?.label || 'Related Literature'
          "
          :emptyValueBehavior="
            jurisdictionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.emptyValueBehavior
          "
          :tooltip="
            jurisdictionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Related Literature'
            )?.tooltip
          "
          mode="id"
        />
      </section>
    </template>

    <template #search-links>
      <template
        v-if="
          courtDecisionCountLoading ||
          domesticInstrumentCountLoading ||
          (courtDecisionCount !== 0 && courtDecisionCount !== null) ||
          (domesticInstrumentCount !== 0 && domesticInstrumentCount !== null)
        "
      >
        <span class="label !mb-4 !mt-0.5"
          >Related Data <InfoTooltip :text="tooltip"
        /></span>

        <template
          v-if="courtDecisionCountLoading || domesticInstrumentCountLoading"
        >
          <LoadingBar />
        </template>
        <template v-else>
          <NuxtLink
            v-if="courtDecisionCount !== 0 && courtDecisionCount !== null"
            :to="{
              name: 'search',
              query: {
                type: 'Court Decisions',
                jurisdiction: jurisdictionData?.Name || '',
              },
            }"
            class="no-underline !mb-2"
          >
            <UButton
              class="link-button"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
            >
              <span class="break-words text-left">
                <template v-if="courtDecisionCount !== null">
                  See {{ courtDecisionCount }} court decision{{
                    courtDecisionCount === 1 ? '' : 's'
                  }}
                  from {{ jurisdictionData?.Name || 'N/A' }}
                </template>
                <template v-else>
                  All court decisions from {{ jurisdictionData?.Name || 'N/A' }}
                </template>
              </span>
            </UButton>
          </NuxtLink>

          <NuxtLink
            v-if="
              domesticInstrumentCount !== 0 && domesticInstrumentCount !== null
            "
            :to="{
              name: 'search',
              query: {
                type: 'Domestic Instruments',
                jurisdiction: jurisdictionData?.Name || '',
              },
            }"
            class="no-underline"
          >
            <UButton
              class="link-button"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
            >
              <span class="break-words text-left">
                <template v-if="domesticInstrumentCount !== null">
                  See {{ domesticInstrumentCount }} domestic instrument{{
                    domesticInstrumentCount === 1 ? '' : 's'
                  }}
                  from {{ jurisdictionData?.Name || 'N/A' }}
                </template>
                <template v-else>
                  All domestic instruments from
                  {{ jurisdictionData?.Name || 'N/A' }}
                </template>
              </span>
            </UButton>
          </NuxtLink>
        </template>
      </template>
    </template>
  </BaseDetailLayout>
  <JurisdictionComparisonLink
    v-if="jurisdictionData"
    :formattedJurisdiction="jurisdictionData"
  />
  <ClientOnly>
    <JurisdictionQuestions
      v-if="jurisdictionData?.Name"
      :formattedJurisdiction="[jurisdictionData.Name]"
    />
    <template #fallback>
      <div class="px-6">
        <div
          class="mx-auto"
          style="max-width: var(--container-width); width: 100%"
        >
          <div class="col-span-12">
            <UCard class="cold-ucard">
              <div>
                <h2 class="mt-2 mb-8">
                  Questions and Answers
                  {{
                    jurisdictionData?.Name ? `for ${jurisdictionData.Name}` : ''
                  }}
                </h2>
                <div class="flex flex-col py-8 space-y-3 ml-8">
                  <LoadingBar />
                  <LoadingBar />
                  <LoadingBar />
                </div>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </template>
  </ClientOnly>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
// import JurisdictionComparison from '@/components/jurisdiction-comparison/JurisdictionComparison.vue'
import JurisdictionComparisonLink from '@/components/ui/JurisdictionComparisonLink.vue'
import JurisdictionQuestions from '@/components/content/JurisdictionQuestions.vue'
import RelatedLiterature from '@/components/literature/RelatedLiterature.vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import { useJurisdiction } from '@/composables/useJurisdiction'
import {
  useDomesticInstrumentsCount,
  useCourtDecisionsCount,
} from '@/composables/useJurisdictionCounts'
import { useLiteratures} from '@/composables/useLiteratures'
import { useSpecialists } from '@/composables/useSpecialists'
import { jurisdictionConfig } from '@/config/pageConfigs'
import { useHead } from '#app'

const tooltip = jurisdictionConfig.keyLabelPairs.find(
  (pair) => pair.key === 'Related Data'
)?.tooltip

const route = useRoute()
const router = useRouter()

const { keyLabelPairs, valueClassMap } = jurisdictionConfig

const compareJurisdiction = ref(null)

const {
  isLoading: isJurisdictionLoading,
  data: jurisdictionData,
  error,
} = useJurisdiction(computed(() => route.params.id))

// const {
//   data: literatures,
//   isLoading: literatureLoading,
//   error: literatureError,
// } = useLiteratures(computed(() => jurisdictionData.value?.Literature))

// const {
//   data: specialists,
//   isLoading: specialistsLoading,
//   error: specialistsError,
// } = useSpecialists(computed(() => jurisdictionData.value?.Name))

const {
  data: courtDecisionCount,
  isLoading: courtDecisionCountLoading,
  error: courtDecisionCountError,
} = useCourtDecisionsCount(computed(() => jurisdictionData.value?.Name))

const {
  data: domesticInstrumentCount,
  isLoading: domesticInstrumentCountLoading,
  error: domesticInstrumentCountError,
} = useDomesticInstrumentsCount(computed(() => jurisdictionData.value?.Name))

// Remove Legal Family from keyLabelPairs for detail display
const keyLabelPairsWithoutLegalFamily = computed(() =>
  keyLabelPairs.filter((pair) => pair.key !== 'Legal Family')
)

// Set compare jurisdiction from query parameter
compareJurisdiction.value = route.query.c || null

const isLoading = computed(
  () =>
    isJurisdictionLoading ||
    // literatureLoading ||
    // specialistsLoading ||
    courtDecisionCountLoading ||
    domesticInstrumentCountLoading
)

// Set dynamic page title based on 'Name'
watch(
  jurisdictionData,
  (newVal) => {
    if (!newVal) return
    const name = newVal.Name
    const pageTitle =
      name && name.trim()
        ? `${name} Country Report — CoLD`
        : 'Jurisdiction Country Report — CoLD'
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

// Handle errors from any of the queries
watch(
  [
    error,
    domesticInstrumentCountError,
    courtDecisionCountError,
    //literatureError, specialistsError
  ],
  (errors) => {
    const firstError = errors.filter(Boolean)?.[0]
    if (firstError) {
      if (firstError.message === 'no entry found with the specified id') {
        router.push({
          path: '/error',
          query: { message: 'Jurisdiction not found' },
        })
      } else {
        console.error('Error fetching data:', firstError)
      }
    }
  }
)
</script>
