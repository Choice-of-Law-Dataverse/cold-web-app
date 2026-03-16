<template>
  <ResultCard :result-data="displayData" :card-type="cardType">
    <div class="flex w-full flex-col gap-0">
      <template v-for="(field, index) in visibleFields" :key="field.key">
        <template v-if="$slots[field.key]">
          <slot
            :name="field.key"
            :value="getFieldValue(field)"
            :label="getFieldLabel(field)"
            :classes="getFieldClasses(index)"
          />
        </template>

        <DetailRow v-else :label="getFieldLabel(field)">
          <TitleWithActions
            v-if="index === 0 && pdfConfig"
            :title-class="getFieldClasses(index)"
          >
            {{ formatFieldValue(field) }}
            <InlineImage :field="field" :display-data="displayData" />
            <template #actions>
              <PdfLink
                :pdf-field="resolvedPdfField"
                :record-id="String(displayData.id)"
                :folder-name="pdfConfig.folderName"
              />
            </template>
          </TitleWithActions>

          <div v-else :class="getFieldClasses(index)">
            {{ formatFieldValue(field) }}
            <InlineImage :field="field" :display-data="displayData" />
          </div>
        </DetailRow>
      </template>

      <slot name="after-fields" />
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import InlineImage from "@/components/search-results/InlineImage.vue";
import {
  getEntityConfigByTable,
  type SearchCardField,
} from "@/config/entityRegistry";
import { camelCaseToLabel } from "@/utils/camelCaseToLabel";
import { formatDate, extractYear } from "@/utils/format";
import type { AnySearchResult, AnySearchResultKey } from "@/types/search";

const props = defineProps<{
  resultData: AnySearchResult;
  cardType: string;
}>();

function field(data: AnySearchResult, key: AnySearchResultKey): unknown {
  return data[key as keyof typeof data];
}

const entityConfig = computed(() => getEntityConfigByTable(props.cardType));
const searchCard = computed(() => entityConfig.value?.searchCard);
const pdfConfig = computed(() => searchCard.value?.pdf);

const displayData = computed<AnySearchResult>(() => {
  if (searchCard.value?.processData) {
    return searchCard.value.processData(props.resultData);
  }
  return props.resultData;
});

const visibleFields = computed(() => {
  if (!searchCard.value) return [];
  return searchCard.value.fields.filter((f) => {
    const value = getFieldValue(f);
    return value && value !== "NA" && value !== "";
  });
});

function getFieldValue(f: SearchCardField): unknown {
  const value = field(displayData.value, f.key);
  if ((!value || value === "NA") && f.fallback) {
    return f.fallback(props.resultData);
  }
  return value;
}

function getFieldLabel(f: SearchCardField): string {
  if (f.label) return f.label;
  const overrides = entityConfig.value?.labelOverrides ?? {};
  return overrides[f.key] ?? camelCaseToLabel(f.key);
}

function getFieldClasses(index: number): string[] {
  const sizeClass = index === 0 ? "result-value-medium" : "result-value-small";
  return [sizeClass, "text-sm leading-relaxed whitespace-normal"];
}

function formatFieldValue(f: SearchCardField): string {
  const value = getFieldValue(f);
  if (value === null || value === undefined || value === "") return "";
  if (f.format === "year") return extractYear(String(value)) ?? String(value);
  if (f.format === "date") return formatDate(String(value)) ?? String(value);
  return String(value);
}

const resolvedPdfField = computed(() => {
  if (!pdfConfig.value) return undefined;
  for (const key of pdfConfig.value.sourceFields) {
    const val = field(props.resultData, key);
    if (val) return val;
  }
  return undefined;
});
</script>
