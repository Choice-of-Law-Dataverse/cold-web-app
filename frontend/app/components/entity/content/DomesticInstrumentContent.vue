<template>
  <EntityContent base-path="/domestic-instrument" :data="data">
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
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import type { DomesticInstrument } from "@/types/entities/domestic-instrument";
import { isTruthy } from "@/types/entities/domestic-instrument";

const props = defineProps<{
  data: DomesticInstrument;
}>();

function isCompatible(
  field:
    | "compatibleWithTheUncitralModelLaw"
    | "compatibleWithTheHcchPrinciples",
): boolean {
  return isTruthy(props.data[field]);
}
</script>
