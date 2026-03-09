<template>
  <div>
    <h1 v-if="data?.abbreviation" class="sr-only">
      {{ data.abbreviation }}
    </h1>
    <BaseDetailLayout
      table="Regional Instruments"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <RegionalInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.abbreviation as string]"
      fallback="Regional Instrument"
    />

    <EntityFeedback
      entity-type="regional_instrument"
      :entity-id="instrumentId"
      :entity-title="(data?.abbreviation as string) || undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import RegionalInstrumentContent from "@/components/entity/content/RegionalInstrumentContent.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/regional-instrument",
  instrumentId,
);
</script>
