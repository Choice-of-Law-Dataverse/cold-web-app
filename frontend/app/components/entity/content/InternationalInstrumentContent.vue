<template>
  <EntityContent base-path="/international-instrument" :data="data">
    <template #name="{ value, label }">
      <DetailRow :label="label">
        <TitleWithActions>
          {{ value }}
          <template #actions>
            <PdfLink
              :pdf-field="data.attachment"
              :record-id="String(data.coldId || '')"
              folder-name="international-instruments"
            />
            <SourceExternalLink :source-url="data.displayUrl" />
          </template>
        </TitleWithActions>
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
import type { InternationalInstrument } from "@/types/entities/international-instrument";

defineProps<{
  data: InternationalInstrument;
}>();
</script>
