<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedLegalInstrument"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Domestic Instrument"
  >
    <!-- Slot for Amended by -->
    <template #amended-by="{ value }">
      <div :class="valueClassMap['Amended by']">
        <SectionRenderer
          v-if="value"
          :id="value"
          section="Amended by"
          :sectionLabel="
            computedKeyLabelPairs.find((pair) => pair.key === 'Amended by')
              ?.label
          "
          :sectionTooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Amended by')
              ?.tooltip
          "
          table="Domestic Instruments"
          class="mb-8"
        />
      </div>
    </template>
    <!-- Slot for Amends -->
    <template #amends="{ value }">
      <div :class="valueClassMap['Amends']">
        <SectionRenderer
          v-if="value"
          :id="value"
          section="Amends"
          :sectionLabel="
            computedKeyLabelPairs.find((pair) => pair.key === 'Amends')?.label
          "
          :sectionTooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Amends')?.tooltip
          "
          table="Domestic Instruments"
          class="mb-8"
        />
      </div>
    </template>
    <!-- Slot for Replaced by -->
    <template #replaced-by="{ value }">
      <div :class="valueClassMap['Replaced by']">
        <SectionRenderer
          v-if="value"
          :id="value"
          section="Replaced by"
          :sectionLabel="
            computedKeyLabelPairs.find((pair) => pair.key === 'Replaced by')
              ?.label
          "
          :sectionTooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Replaced by')
              ?.tooltip
          "
          table="Domestic Instruments"
          class="mb-8"
        />
      </div>
    </template>
    <!-- Slot for Replaces -->
    <template #replaces="{ value }">
      <div :class="valueClassMap['Replaces']">
        <SectionRenderer
          v-if="value"
          :id="value"
          section="Replaces"
          :sectionLabel="
            computedKeyLabelPairs.find((pair) => pair.key === 'Replaces')?.label
          "
          :sectionTooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Replaces')
              ?.tooltip
          "
          table="Domestic Instruments"
          class="mb-8"
        />
      </div>
    </template>
    <!-- Slot for Compatibility section -->
    <template #compatibility>
      <div
        v-if="
          processedLegalInstrument &&
          (processedLegalInstrument[
            'Compatible With the UNCITRAL Model Law?'
          ] === true ||
            processedLegalInstrument[
              'Compatible With the UNCITRAL Model Law?'
            ] === 'true' ||
            processedLegalInstrument['Compatible With the HCCH Principles?'] ===
              true ||
            processedLegalInstrument['Compatible With the HCCH Principles?'] ===
              'true')
        "
        class="result-value-small section-gap"
      >
        <p class="label mt-12">
          Compatible with
          <InfoTooltip
            v-if="
              computedKeyLabelPairs.find((pair) => pair.key === 'Compatibility')
                ?.tooltip
            "
            :text="
              computedKeyLabelPairs.find((pair) => pair.key === 'Compatibility')
                ?.tooltip
            "
          />
        </p>
        <span
          v-if="
            processedLegalInstrument &&
            (processedLegalInstrument[
              'Compatible With the UNCITRAL Model Law?'
            ] === true ||
              processedLegalInstrument[
                'Compatible With the UNCITRAL Model Law?'
              ] === 'true')
          "
        >
          <CompatibleLabel label="UNCITRAL Model Law" />
        </span>
        <span
          v-if="
            processedLegalInstrument &&
            (processedLegalInstrument[
              'Compatible With the HCCH Principles?'
            ] === true ||
              processedLegalInstrument[
                'Compatible With the HCCH Principles?'
              ] === 'true')
          "
        >
          <CompatibleLabel label="HCCH Principles" />
        </span>
      </div>
    </template>
    <!-- Slot for Legal provisions -->
    <template #domestic-legal-provisions="{ value }">
      <!-- Only render if value exists and is not "N/A" -->
      <section
        v-if="value && value.trim() && value.trim() !== 'N/A'"
        class="section-gap p-0 m-0"
      >
        <p class="label mt-12 mb-[-24px]">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions'
            )?.label || 'Selected Provisions'
          }}
          <InfoTooltip
            v-if="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
            :text="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.tooltip
            "
          />
        </p>
        <div :class="valueClassMap['Domestic Legal Provisions']">
          <div v-if="value && value.trim()">
            <LegalProvision
              v-for="(provisionId, index) in getSortedProvisionIds(value)"
              :key="index"
              :provisionId="provisionId"
              :textType="textType"
              :instrumentTitle="
                processedLegalInstrument
                  ? processedLegalInstrument['Abbreviation'] ||
                    processedLegalInstrument['Title (in English)']
                  : ''
              "
              @update:hasEnglishTranslation="hasEnglishTranslation = $event"
            />
          </div>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
  <CountryReportLink :processedAnswerData="processedLegalInstrument" />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import LegalProvision from '@/components/legal/LegalProvision.vue'
import InfoTooltip from '@/components/ui/InfoTooltip.vue'
import SectionRenderer from '@/components/legal/SectionRenderer.vue'
import CompatibleLabel from '@/components/ui/CompatibleLabel.vue'
import CountryReportLink from '@/components/ui/CountryReportLink.vue'
import { useApiFetch } from '@/composables/useApiFetch'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { legalInstrumentConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()
const textType = ref('Full Text of the Provision (English Translation)')
const hasEnglishTranslation = ref(false)

const { loading, error, data: legalInstrument, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  legalInstrument,
  legalInstrumentConfig
)

const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) {
    return null
  }
  return {
    ...legalInstrument.value,
    'Title (in English)':
      legalInstrument.value['Title (in English)'] ||
      legalInstrument.value['Official Title'],
  }
})

// Set dynamic page title based on 'Title (in English)'
watch(
  processedLegalInstrument,
  (newVal) => {
    if (!newVal) return
    const titleEn = newVal['Title (in English)']
    const pageTitle =
      titleEn && titleEn.trim()
        ? `${titleEn} — CoLD`
        : 'Domestic Instrument — CoLD'
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

onMounted(async () => {
  try {
    await fetchData({
      table: 'Domestic Instruments',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `Domestic instrument not found` },
      })
    } else {
      console.error('Error fetching legal instrument:', err)
    }
  }
})

/**
 * Returns provision IDs sorted by their "Ranking (Display Order)" value.
 * The backend now supplies a field that can associate ordering with provisions.
 * Assumptions:
 *  - processedLegalInstrument may contain a mapping object
 *    like "Ranking (Display Order)": "provA:1,provB:2" OR "1:provA,2:provB" OR JSON array/object.
 *  - If the ranking field is absent or unparsable, we fall back to the original order.
 */
function getSortedProvisionIds(rawValue) {
  if (!rawValue) return []
  const ids = rawValue
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)

  const rankingRaw = processedLegalInstrument.value?.['Ranking (Display Order)']
  if (!rankingRaw) return ids

  // Try a few parsing strategies
  let rankingMap = {}
  try {
    if (typeof rankingRaw === 'string') {
      // Strategy 0: Simple numeric CSV (e.g. "2,1,3") aligned by index to ids
      if (
        typeof rankingRaw === 'string' &&
        /^(\s*\d+\s*)([,;]\s*\d+\s*)*$/.test(rankingRaw.trim())
      ) {
        const nums = rankingRaw.split(/[,;]+/).map((n) => Number(n.trim()))
        if (nums.length === ids.length) {
          ids.forEach((pid, idx) => {
            const r = nums[idx]
            if (!isNaN(r)) rankingMap[pid] = r
          })
        }
      }

      // Try JSON first
      if (
        rankingRaw.trim().startsWith('{') ||
        rankingRaw.trim().startsWith('[')
      ) {
        const parsed = JSON.parse(rankingRaw)
        if (Array.isArray(parsed)) {
          // If array, assume it is in order already
          parsed.forEach((pid, idx) => {
            if (typeof pid === 'string') rankingMap[pid] = idx + 1
          })
        } else if (parsed && typeof parsed === 'object') {
          rankingMap = Object.fromEntries(
            Object.entries(parsed).map(([k, v]) => {
              // Accept either key=provisionId, value=rank OR key=rank, value=provisionId
              if (ids.includes(k) && !isNaN(Number(v))) {
                return [k, Number(v)]
              }
              if (ids.includes(String(v)) && !isNaN(Number(k))) {
                return [String(v), Number(k)]
              }
              return [k, Number(v)] // fallback
            })
          )
        }
      } else {
        // Handle simple delimited patterns: "provA:1,provB:2" or "1:provA,2:provB"
        rankingRaw.split(/[,;]+/).forEach((pair) => {
          const [a, b] = pair.split(':').map((s) => s && s.trim())
          if (!a || !b) return
          if (ids.includes(a) && !isNaN(Number(b))) {
            rankingMap[a] = Number(b)
          } else if (ids.includes(b) && !isNaN(Number(a))) {
            rankingMap[b] = Number(a)
          }
        })
      }
    } else if (Array.isArray(rankingRaw)) {
      rankingRaw.forEach((pid, idx) => {
        if (typeof pid === 'string') rankingMap[pid] = idx + 1
      })
    } else if (rankingRaw && typeof rankingRaw === 'object') {
      rankingMap = Object.fromEntries(
        Object.entries(rankingRaw).map(([k, v]) => {
          if (ids.includes(k) && !isNaN(Number(v))) return [k, Number(v)]
          if (ids.includes(String(v)) && !isNaN(Number(k)))
            return [String(v), Number(k)]
          return [k, Number(v)]
        })
      )
    }
  } catch (e) {
    console.warn('Failed to parse Ranking (Display Order):', e)
  }

  // If we got no usable ranking numbers, keep original order
  const hasNumbers = Object.values(rankingMap).some(
    (n) => typeof n === 'number' && !isNaN(n)
  )
  if (!hasNumbers) return ids

  return [...ids].sort((a, b) => {
    const ra = rankingMap[a]
    const rb = rankingMap[b]
    if (ra == null && rb == null) return 0
    if (ra == null) return 1 // unranked go last
    if (rb == null) return -1
    return ra - rb
  })
}
</script>
