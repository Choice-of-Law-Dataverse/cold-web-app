<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="jurisdictionData"
    :keyLabelPairs="keyLabelPairsWithoutLegalFamily"
    :valueClassMap="valueClassMap"
    :formattedJurisdiction="[jurisdictionData?.Name]"
  >
    <!-- Specialists Section -->
    <section>
      <span class="label">Specialists</span>
      <template v-if="specialists.length">
        <ul>
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
      <section>
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
        />
      </section>
    </template>

    <template #search-links>
      <span class="label !mt-[-36px] !mb-5">Related Data</span>
      <NuxtLink
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
            All court decisions from {{ jurisdictionData?.Name || 'N/A' }}
          </span>
        </UButton>
      </NuxtLink>

      <NuxtLink
        :to="{
          name: 'search',
          query: {
            type: 'Legal Instruments',
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
            All legal instruments from
            {{ jurisdictionData?.Name || 'N/A' }}
          </span>
        </UButton>
      </NuxtLink>
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
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import JurisdictionComparison from '~/components/jurisdiction-comparison/JurisdictionComparison.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import { useJurisdiction } from '~/composables/useJurisdiction'
import { jurisdictionConfig } from '~/config/pageConfigs'

const route = useRoute()
const router = useRouter()
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
