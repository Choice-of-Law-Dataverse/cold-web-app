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
                :record-id="displayData.id as string"
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

const props = defineProps<{
  resultData: Record<string, unknown>;
  cardType: string;
}>();

const entityConfig = computed(() => getEntityConfigByTable(props.cardType));
const searchCard = computed(() => entityConfig.value?.searchCard);
const pdfConfig = computed(() => searchCard.value?.pdf);

const displayData = computed<Record<string, unknown>>(() => {
  if (searchCard.value?.processData) {
    return searchCard.value.processData(props.resultData);
  }
  return props.resultData;
});

const visibleFields = computed(() => {
  if (!searchCard.value) return [];
  return searchCard.value.fields.filter((field) => {
    const value = getFieldValue(field);
    return value && value !== "NA" && value !== "";
  });
});

function getFieldValue(field: SearchCardField): unknown {
  const value = displayData.value[field.key];
  if ((!value || value === "NA") && field.fallback) {
    return field.fallback(props.resultData);
  }
  return value;
}

function getFieldLabel(field: SearchCardField): string {
  if (field.label) return field.label;
  const overrides = entityConfig.value?.labelOverrides ?? {};
  return overrides[field.key] ?? camelCaseToLabel(field.key);
}

function getFieldClasses(index: number): string[] {
  const sizeClass = index === 0 ? "result-value-medium" : "result-value-small";
  return [sizeClass, "text-sm leading-relaxed whitespace-normal"];
}

function formatFieldValue(field: SearchCardField): string {
  const value = getFieldValue(field);
  if (value === null || value === undefined || value === "") return "";
  if (field.format === "year")
    return extractYear(String(value)) ?? String(value);
  if (field.format === "date")
    return formatDate(String(value)) ?? String(value);
  return String(value);
}

const resolvedPdfField = computed(() => {
  if (!pdfConfig.value) return undefined;
  for (const fieldName of pdfConfig.value.sourceFields) {
    if (props.resultData[fieldName]) return props.resultData[fieldName];
  }
  return undefined;
});
</script>
