<template>
  <div>
    <h1 v-if="data?.titleInEnglish" class="sr-only">
      {{ data.titleInEnglish }}
    </h1>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="domestic_instrument"
      :entity-id="coldId"
      :entity-title="data?.titleInEnglish ?? undefined"
    >
      <DomesticInstrumentContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.titleInEnglish]"
      fallback="Domestic Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DomesticInstrumentContent from "@/components/entity/content/DomesticInstrumentContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/domestic-instrument",
  coldId,
);
</script>
