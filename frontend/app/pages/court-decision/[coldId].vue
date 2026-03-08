<template>
  <div>
    <h1 v-if="courtDecision?.caseTitle" class="sr-only">
      {{ courtDecision.caseTitle }}
    </h1>
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
      <template #casetitle="{ value }">
        <DetailRow
          :label="courtDecisionLabels.caseTitle"
          :tooltip="courtDecisionTooltips.caseTitle"
        >
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="courtDecision?.officialSourcePdf"
                :record-id="courtDecisionId"
                folder-name="court-decisions"
              />
              <SourceExternalLink
                :source-url="courtDecision?.officialSourceUrl || ''"
              />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #domesticlegalprovisions="{ value }">
        <DetailRow
          v-if="value"
          :label="courtDecisionLabels.domesticLegalProvisions"
          :tooltip="courtDecisionTooltips.domesticLegalProvisions"
        >
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>

      <template #quote>
        <DetailRow
          v-if="
            courtDecision &&
            (courtDecision.quote || courtDecision.translatedExcerpt)
          "
          :label="courtDecisionLabels.quote"
          :tooltip="courtDecisionTooltips.quote"
        >
          <div>
            <div
              v-if="
                courtDecision?.hasEnglishQuoteTranslation &&
                courtDecision?.quote &&
                courtDecision.quote.trim() !== ''
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
                size="sm"
                checked-icon="i-material-symbols-translate"
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
                  courtDecision?.quote &&
                  courtDecision.quote.trim() !== ""
                    ? courtDecision.translatedExcerpt
                    : courtDecision?.quote || courtDecision?.translatedExcerpt
                }}
              </p>
            </div>
          </div>
        </DetailRow>
      </template>
      <!-- Custom rendering for Related Questions section -->
      <template #relatedquestions>
        <DetailRow
          v-if="relatedQuestions.length"
          :label="courtDecisionLabels.relatedQuestions"
          :tooltip="courtDecisionTooltips.relatedQuestions"
          variant="question"
        >
          <RelatedItemsList :items="relatedQuestions" base-path="/question" />
        </DetailRow>
      </template>
      <template #relatedliterature>
        <DetailRow
          :label="courtDecisionLabels.relatedLiterature"
          :tooltip="courtDecisionTooltips.relatedLiterature"
          variant="literature"
        >
          <RelatedItemsList
            :items="relatedLiterature"
            base-path="/literature"
            :empty-value-behavior="{
              action: 'display',
              fallback: 'No related literature available',
            }"
          />
        </DetailRow>
      </template>

      <template #originaltext="{ value }">
        <DetailRow
          v-if="value && (value as string).trim() !== ''"
          :label="courtDecisionLabels.originalText"
        >
          <div>
            <p class="result-value-small">
              {{
                showFullText || (value as string).length <= 400
                  ? value
                  : (value as string).slice(0, 400) + "…"
              }}
            </p>
            <ShowMoreLess
              v-if="(value as string).length > 400"
              v-model:is-expanded="showFullText"
            />
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="primaryJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="primaryJurisdiction?.name ?? undefined"
        />
        <LastModified :date="courtDecision?.updatedAt" />
      </template>

      <template #search-links />
    </BaseDetailLayout>

    <UAlert v-if="error" type="error" class="max-w-container mx-auto mt-4">
      {{ error }}
    </UAlert>

    <PageSeoMeta
      :title-candidates="[
        courtDecision?.caseTitle !== 'Not found'
          ? courtDecision?.caseTitle
          : null,
        courtDecision?.caseCitation,
      ]"
      fallback="Court Decision"
    />

    <EntityFeedback
      entity-type="court_decision"
      :entity-id="courtDecisionId"
      :entity-title="courtDecision?.caseTitle as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import LastModified from "@/components/ui/LastModified.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useCourtDecision } from "@/composables/useRecordDetails";
import { courtDecisionLabels } from "@/config/labels";
import { courtDecisionTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

defineProps({
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px] mt-2 ml-[-12px]",
  },
});

const route = useRoute();
const courtDecisionId = ref(route.params.coldId as string);

const {
  data: courtDecision,
  isLoading,
  error,
} = useCourtDecision(courtDecisionId);

const showEnglishQuote = ref(true);
const showFullText = ref(false);

const primaryJurisdiction = computed(
  () => courtDecision.value?.relations.jurisdictions[0] ?? null,
);

const relatedQuestions = computed<RelatedItem[]>(() =>
  (courtDecision.value?.relations.questions ?? []).map((q) => ({
    id: q.coldId || String(q.id),
    title: q.question || q.coldId || String(q.id),
  })),
);

const relatedLiterature = computed<RelatedItem[]>(() =>
  (courtDecision.value?.relations.literature ?? [])
    .filter((lit) => !lit.oupJdChapter)
    .map((lit) => ({
      id: lit.coldId || String(lit.id),
      title: lit.title || String(lit.id),
    })),
);
</script>
