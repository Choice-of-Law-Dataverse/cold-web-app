<template>
  <div>
    <h1 v-if="data?.abbreviation" class="sr-only">
      {{ data.abbreviation }}
    </h1>
    <BaseDetailLayout
      table="Regional Instruments"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <template #title-actions>
        <template v-if="data">
          <PdfLink
            :pdf-field="data.attachment"
            :record-id="String(data.coldId || '')"
            folder-name="regional-instruments"
          />
          <SourceExternalLink :source-url="data.url" />
        </template>
      </template>

      <RegionalInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.abbreviation]"
      fallback="Regional Instrument"
    />

    <EntityFeedback
      entity-type="regional_instrument"
      :entity-id="coldId"
      :entity-title="data?.abbreviation ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import RegionalInstrumentContent from "@/components/entity/content/RegionalInstrumentContent.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/regional-instrument",
  coldId,
);
</script>
