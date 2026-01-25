<template>
  <div>
    <BaseDetailLayout
      table="Court Decisions"
      :loading="isLoading"
      :error="error"
      :data="courtDecision || {}"
      :labels="courtDecisionLabels"
      :tooltips="courtDecisionTooltips"
      :show-suggest-edit="true"
    >
      <!-- Case Title with PDF and Source Link -->
      <template #case-title="{ value }">
        <DetailRow
          :label="courtDecisionLabels['Case Title']"
          :tooltip="courtDecisionTooltips['Case Title']"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="result-value-small flex-1">
              {{ value }}
            </div>
            <div class="flex flex-shrink-0 items-center gap-3">
              <PdfLink
                :pdf-field="courtDecision?.['Official Source (PDF)']"
                :record-id="route.params.id as string"
                folder-name="court-decisions"
              />
              <SourceExternalLink
                :source-url="courtDecision?.['Official Source (URL)'] || ''"
              />
            </div>
          </div>
        </DetailRow>
      </template>

      <template #domestic-legal-provisions="{ value }">
        <DetailRow
          v-if="value"
          :label="courtDecisionLabels['Domestic Legal Provisions']"
          :tooltip="courtDecisionTooltips['Domestic Legal Provisions']"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </DetailRow>
      </template>

      <template #quote>
        <DetailRow
          v-if="
            courtDecision &&
            (courtDecision['Quote'] || courtDecision['Translated Excerpt'])
          "
          :label="courtDecisionLabels['Quote']"
          :tooltip="courtDecisionTooltips['Quote']"
        >
          <div>
            <div
              v-if="
                courtDecision?.hasEnglishQuoteTranslation &&
                courtDecision?.Quote &&
                courtDecision.Quote.trim() !== ''
              "
              class="mb-2 flex items-center gap-1"
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
              <USwitch
                v-model="showEnglishQuote"
                size="xs"
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
            <div>
              <p class="result-value-small whitespace-pre-line">
                {{
                  showEnglishQuote &&
                  courtDecision?.hasEnglishQuoteTranslation &&
                  courtDecision?.Quote &&
                  courtDecision.Quote.trim() !== ""
                    ? courtDecision["Translated Excerpt"]
                    : courtDecision?.Quote ||
                      courtDecision?.["Translated Excerpt"]
                }}
              </p>
            </div>
          </div>
        </DetailRow>
      </template>
      <!-- Custom rendering for Related Questions section -->
      <template #related-questions="{ value }">
        <DetailRow
          v-if="value"
          :label="courtDecisionLabels['Related Questions']"
          :tooltip="courtDecisionTooltips['Related Questions']"
          variant="question"
        >
          <LazyRelatedQuestions
            hydrate-on-visible
            :jurisdiction-code="
              courtDecision?.['Jurisdictions Alpha-3 Code'] || ''
            "
            :questions="value"
          />
        </DetailRow>
      </template>
      <template #related-literature>
        <DetailRow
          :label="courtDecisionLabels['Related Literature']"
          :tooltip="courtDecisionTooltips['Related Literature']"
          variant="literature"
        >
          <LazyRelatedLiterature
            hydrate-on-visible
            :themes="courtDecision?.themes || ''"
            :mode="'themes'"
            :oup-filter="'noOup'"
            :empty-value-behavior="{
              action: 'display',
              fallback: 'No related literature available',
            }"
          />
        </DetailRow>
      </template>

      <template #original-text="{ value }">
        <DetailRow
          v-if="value && value.trim() !== ''"
          :label="courtDecisionLabels['Original Text']"
        >
          <div>
            <div v-if="!showFullText && value.length > 400">
              <p class="result-value-small">
                {{ value.slice(0, 400)
                }}<span v-if="value.length > 400">…</span>
              </p>
              <button
                class="bg-cold-teal/5 text-cold-teal hover:bg-cold-teal/10 inline-flex items-center rounded-full px-3 py-1 text-sm transition-colors"
                :style="{ fontWeight: '500' }"
                @click="showFullText = true"
              >
                Show more
              </button>
            </div>
            <div v-else>
              <p class="result-value-small">
                {{ value }}
              </p>
              <button
                v-if="value.length > 400"
                class="bg-cold-teal/5 text-cold-teal hover:bg-cold-teal/10 inline-flex items-center rounded-full px-3 py-1 text-sm transition-colors"
                :style="{ fontWeight: '500' }"
                @click="showFullText = false"
              >
                Show less
              </button>
            </div>
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="courtDecision?.['Last Modified']" />
        <LazyCountryReportBanner
          hydrate-on-visible
          :jurisdiction-code="courtDecision?.['Jurisdictions Alpha-3 Code']"
        />
      </template>

      <template #search-links />
    </BaseDetailLayout>

    <UAlert v-if="error" type="error" class="max-w-container mx-auto mt-4">
      {{ error }}
    </UAlert>

    <PageSeoMeta
      :title-candidates="[
        courtDecision?.['Case Title'] !== 'Not found'
          ? courtDecision?.['Case Title']
          : null,
        courtDecision?.['Case Citation'],
      ]"
      fallback="Court Decision"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useCourtDecision } from "@/composables/useRecordDetails";
import { courtDecisionLabels } from "@/config/labels";
import { courtDecisionTooltips } from "@/config/tooltips";

defineProps({
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px] mt-2 ml-[-12px]",
  },
});

const route = useRoute();

const {
  data: courtDecision,
  isLoading,
  error,
} = useCourtDecision(computed(() => route.params.id as string));

const showEnglishQuote = ref(true);
const showFullText = ref(false);
</script>
