<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="jurisdictionData"
    :keyLabelPairs="keyLabelPairsWithoutLegalFamily"
    :valueClassMap="valueClassMap"
    :formattedJurisdiction="[jurisdictionData?.Name]"
  >
    <!-- Specialists Section -->
    <section class="section-gap p-0 m-0">
      <span class="label">
        {{
          keyLabelPairs.find((pair) => pair.key === 'Specialist')?.label ||
          'Specialists'
        }}
        <InfoTooltip
          v-if="
            keyLabelPairs.find((pair) => pair.key === 'Specialist')?.tooltip
          "
          :text="
            keyLabelPairs.find((pair) => pair.key === 'Specialist')?.tooltip
          "
          class="ml-1 align-middle"
        />
      </span>
      <template v-if="specialists.length">
        <ul class="section-gap p-0 m-0">
          <li
            v-for="specialist in specialists"
            :key="specialist.Specialist"
            class="result-value-small"
          >
            {{ specialist.Specialist }}
          </li>
        </ul>
      </template>
      <p v-else class="result-value-small">
        {{
          keyLabelPairs.find((pair) => pair.key === 'Specialist')
            ?.emptyValueBehavior?.fallback || 'No specialists available'
        }}
      </p>
    </section>

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
          countsLoading ||
          (courtDecisionCount !== 0 && courtDecisionCount !== null) ||
          (domesticInstrumentCount !== 0 && domesticInstrumentCount !== null)
        "
      >
        <span class="label !mb-4 !mt-0.5"
          >Related Data <InfoTooltip :text="tooltip"
        /></span>

        <template v-if="countsLoading">
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

  <!-- Only render JurisdictionComparison if jurisdictionData is loaded -->
  <JurisdictionComparison
    v-if="!loading && jurisdictionData?.Name"
    :jurisdiction="jurisdictionData.Name"
    :compareJurisdiction="compareJurisdiction"
  />
</template>

<script setup>
import { onMounted, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import JurisdictionComparison from '~/components/jurisdiction-comparison/JurisdictionComparison.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import LoadingBar from '~/components/layout/LoadingBar.vue'
import InfoTooltip from '~/components/ui/InfoTooltip.vue'
import { useJurisdiction } from '~/composables/useJurisdiction'
import { jurisdictionConfig } from '~/config/pageConfigs'
import { useRuntimeConfig, useHead } from '#app'

const tooltip = jurisdictionConfig.keyLabelPairs.find(
  (pair) => pair.key === 'Related Data'
)?.tooltip

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const {
  loading,
  jurisdictionData,
  specialists,
  compareJurisdiction,
  keyLabelPairs,
  valueClassMap,
  fetchJurisdiction,
} = useJurisdiction()

// Remove Legal Family from keyLabelPairs for detail display
const keyLabelPairsWithoutLegalFamily = computed(() =>
  keyLabelPairs.filter((pair) => pair.key !== 'Legal Family')
)

// Set compare jurisdiction from query parameter
compareJurisdiction.value = route.query.c || null

// --- New: State for result counts ---
const courtDecisionCount = ref(null)
const domesticInstrumentCount = ref(null)
const countsLoading = ref(true)

async function fetchResultCount(jurisdiction, table) {
  if (!jurisdiction) return null
  const payload = {
    search_string: '',
    filters: [
      { column: 'jurisdictions', values: [jurisdiction] },
      { column: 'tables', values: [table] },
    ],
    page: 1,
    page_size: 1,
  }
  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    if (!response.ok) throw new Error('Failed to fetch count')
    const data = await response.json()
    return data.total_matches || 0
  } catch (e) {
    console.error('Error fetching result count:', e)
    return null
  }
}

// Fetch counts when jurisdiction changes
watch(
  () => jurisdictionData?.value?.Name,
  async (newName) => {
    if (newName) {
      countsLoading.value = true
      const [courtCount, legalCount] = await Promise.all([
        fetchResultCount(newName, 'Court Decisions'),
        fetchResultCount(newName, 'Domestic Instruments'),
      ])
      courtDecisionCount.value = courtCount
      domesticInstrumentCount.value = legalCount
      countsLoading.value = false
    } else {
      courtDecisionCount.value = null
      domesticInstrumentCount.value = null
      countsLoading.value = false
    }
  },
  { immediate: true }
)

// Set dynamic page title based on 'Name'
watch(
  jurisdictionData,
  (newVal) => {
    if (!newVal) return
    const name = newVal.Name
    const pageTitle = name && name.trim() ? `${name} — CoLD` : 'Jurisdiction — CoLD'
    useHead({ title: pageTitle })
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    const id = route.params.id
    await fetchJurisdiction(id)
  } catch (err) {
    if (err.message === 'no entry found with the specified id') {
      router.push({
        path: '/error',
        query: { message: 'Jurisdiction not found' },
      })
    } else {
      console.error('Error fetching jurisdiction:', err)
    }
  }
})
</script>
