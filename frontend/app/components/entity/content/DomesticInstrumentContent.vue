<template>
  <EntityContent base-path="/domestic-instrument" :data="data">
    <template #titleInEnglish="{ value, label, tooltip }">
      <DetailRow :label="label" :tooltip="tooltip">
        <TitleWithActions>
          {{ value }}
          <template #actions>
            <PdfLink
              :pdf-field="data.sourcePdf"
              :record-id="String(data.coldId || '')"
              folder-name="domestic-instruments"
            />
            <SourceExternalLink :source-url="data.sourceUrl" />
          </template>
        </TitleWithActions>
      </DetailRow>
    </template>

    <template #amendedBy="{ value, label }">
      <DetailRow v-if="value" :label="label">
        <InstrumentLink :id="value as string" table="Domestic Instruments" />
      </DetailRow>
    </template>

    <template #amends="{ value, label }">
      <DetailRow v-if="value" :label="label">
        <InstrumentLink :id="value as string" table="Domestic Instruments" />
      </DetailRow>
    </template>

    <template #replacedBy="{ value, label }">
      <DetailRow v-if="value" :label="label">
        <InstrumentLink :id="value as string" table="Domestic Instruments" />
      </DetailRow>
    </template>

    <template #replaces="{ value, label }">
      <DetailRow v-if="value" :label="label">
        <InstrumentLink :id="value as string" table="Domestic Instruments" />
      </DetailRow>
    </template>

    <template #compatibility="{ value, label, tooltip }">
      <DetailRow
        v-if="
          value &&
          (isCompatible('compatibleWithTheUncitralModelLaw') ||
            isCompatible('compatibleWithTheHcchPrinciples'))
        "
        :label="label"
        :tooltip="tooltip"
      >
        <div class="result-value-small flex gap-2">
          <CompatibleLabel
            v-if="isCompatible('compatibleWithTheUncitralModelLaw')"
            label="UNCITRAL Model Law"
          />
          <CompatibleLabel
            v-if="isCompatible('compatibleWithTheHcchPrinciples')"
            label="HCCH Principles"
          />
        </div>
      </DetailRow>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import { isTruthy } from "@/types/entities/domestic-instrument";

const props = defineProps<{
  data: Record<string, unknown>;
}>();

function isCompatible(
  field:
    | "compatibleWithTheUncitralModelLaw"
    | "compatibleWithTheHcchPrinciples",
): boolean {
  return isTruthy(props.data[field] as string);
}
</script>
