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
      entity-type="regional_instrument"
      :entity-id="coldId"
      :entity-title="data?.abbreviation ?? undefined"
    >
      <RegionalInstrumentContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.abbreviation]"
      fallback="Regional Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import RegionalInstrumentContent from "@/components/entity/content/RegionalInstrumentContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/regional-instrument",
  coldId,
);
</script>
