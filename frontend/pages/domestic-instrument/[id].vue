<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedLegalInstrument"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Domestic Instrument"
    >
      <!-- Slot for Amended by -->
      <template #amended-by="{ value }">
        <div :class="valueClassMap['Amended by']">
          <SectionRenderer
            v-if="value"
            :id="value"
            section="Amended by"
            :section-label="
              computedKeyLabelPairs.find((pair) => pair.key === 'Amended by')
                ?.label
            "
            :section-tooltip="
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
            :section-label="
              computedKeyLabelPairs.find((pair) => pair.key === 'Amends')?.label
            "
            :section-tooltip="
              computedKeyLabelPairs.find((pair) => pair.key === 'Amends')
                ?.tooltip
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
            :section-label="
              computedKeyLabelPairs.find((pair) => pair.key === 'Replaced by')
                ?.label
            "
            :section-tooltip="
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
            :section-label="
              computedKeyLabelPairs.find((pair) => pair.key === 'Replaces')
                ?.label
            "
            :section-tooltip="
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
              processedLegalInstrument[
                'Compatible With the HCCH Principles?'
              ] === true ||
              processedLegalInstrument[
                'Compatible With the HCCH Principles?'
              ] === 'true')
          "
          class="result-value-small section-gap"
        >
          <p class="label mt-12 flex flex-row items-center">
            Compatible with
            <InfoPopover
              v-if="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Compatibility'
                )?.tooltip
              "
              :text="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Compatibility'
                )?.tooltip
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
          class="section-gap m-0 p-0"
        >
          <p class="label mb-[-24px] mt-12 flex flex-row items-center">
            {{
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions'
              )?.label || 'Selected Provisions'
            }}
            <InfoPopover
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
                :provision-id="provisionId"
                :text-type="textType"
                :instrument-title="
                  processedLegalInstrument
                    ? processedLegalInstrument['Abbreviation'] ||
                      processedLegalInstrument['Title (in English)']
                    : ''
                "
                @update:has-english-translation="hasEnglishTranslation = $event"
              />
            </div>
          </div>
        </section>
      </template>
    </BaseDetailLayout>
    <CountryReportLink :processed-answer-data="processedLegalInstrument" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import LegalProvision from '@/components/legal/LegalProvision.vue'
import InfoPopover from '~/components/ui/InfoPopover.vue'
import SectionRenderer from '@/components/legal/SectionRenderer.vue'
import CompatibleLabel from '@/components/ui/CompatibleLabel.vue'
import CountryReportLink from '@/components/ui/CountryReportLink.vue'
import { useRecordDetails } from '@/composables/useRecordDetails'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { legalInstrumentConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const textType = ref('Full Text of the Provision (English Translation)')
const hasEnglishTranslation = ref(false)

// Use TanStack Vue Query for data fetching
const table = ref('Domestic Instruments')
const id = ref(route.params.id)

const { data: legalInstrument, isLoading: loading } = useRecordDetails(
  table,
  id
)

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
