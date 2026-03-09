<template>
  <EntityContent base-path="/regional-instrument" :data="data">
    <template #abbreviation="{ value, label }">
      <DetailRow :label="label">
        <TitleWithActions>
          {{ value }}
          <template #actions>
            <PdfLink
              :pdf-field="data.attachment"
              :record-id="String(data.coldId || '')"
              folder-name="regional-instruments"
            />
            <SourceExternalLink :source-url="data.url" />
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
import type { RegionalInstrument } from "@/types/entities/regional-instrument";

defineProps<{
  data: RegionalInstrument;
}>();
</script>
