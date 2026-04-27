<template>
  <EntityContent base-path="/court-decision" :data="data">
    <template #caseTitle="{ value, label, tooltip }">
      <DetailRow :label="label" :tooltip="tooltip">
        <TitleWithActions>
          {{ value }}
          <template #actions>
            <PdfLink
              :pdf-field="data.officialSourcePdf"
              :record-id="String(data.coldId || '')"
              folder-name="court-decisions"
            />
            <SourceExternalLink
              :source-url="String(data.officialSourceUrl || '')"
            />
          </template>
        </TitleWithActions>
      </DetailRow>
    </template>

    <template #quote="{ label, tooltip }">
      <DetailRow
        v-if="data.quote || data.translatedExcerpt"
        :label="label"
        :tooltip="tooltip"
      >
        <div>
          <div
            v-if="
              data.hasEnglishQuoteTranslation &&
              data.quote &&
              String(data.quote).trim() !== ''
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
          <ResultValue size="sm" as="p" class="whitespace-pre-line">{{
            showEnglishQuote &&
            data.hasEnglishQuoteTranslation &&
            data.quote &&
            String(data.quote).trim() !== ""
              ? data.translatedExcerpt
              : data.quote || data.translatedExcerpt
          }}</ResultValue>
        </div>
      </DetailRow>
    </template>

    <template #originalText="{ value, label }">
      <DetailRow v-if="value && String(value).trim() !== ''" :label="label">
        <div>
          <ResultValue size="sm" as="p">{{
            showFullText || String(value).length <= 400
              ? value
              : String(value).slice(0, 400) + "…"
          }}</ResultValue>
          <ShowMoreLess
            v-if="String(value).length > 400"
            v-model:is-expanded="showFullText"
          />
        </div>
      </DetailRow>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import { ref } from "vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import type { CourtDecision } from "@/types/entities/court-decision";
import ResultValue from "@/components/ui/ResultValue.vue";

defineProps<{
  data: CourtDecision;
}>();

const showEnglishQuote = ref(true);
const showFullText = ref(false);
</script>

<style>
@reference "@/assets/styles.css";

.label-key-provision-article,
.label-key-provision-toggle {
  @apply text-cold-night-alpha inline-flex gap-1 p-0 tracking-wider normal-case;
}

.label-key-provision-article {
  @apply text-sm font-medium;
}

.label-key-provision-toggle {
  @apply text-[0.625rem] font-semibold capitalize;
}
</style>
