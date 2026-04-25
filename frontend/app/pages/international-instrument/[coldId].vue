<template>
  <div>
    <h1 v-if="data?.name" class="sr-only">
      {{ data.name }}
    </h1>
    <BaseDetailLayout
      table="International Instruments"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <InternationalInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <div v-if="hcchAnswers.length" class="mt-8">
      <InternationalInstrumentComparisonTable
        :instrument-name="data?.name ?? ''"
        :instrument-cold-id="data?.coldId ?? coldId"
        :hcch-answers="hcchAnswers"
      />
    </div>

    <PageSeoMeta
      :title-candidates="[data?.name]"
      fallback="International Instrument"
    />

    <EntityFeedback
      entity-type="international_instrument"
      :entity-id="coldId"
      :entity-title="data?.name ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InternationalInstrumentContent from "@/components/entity/content/InternationalInstrumentContent.vue";
import InternationalInstrumentComparisonTable from "@/components/international-instrument/InternationalInstrumentComparisonTable.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/international-instrument",
  coldId,
);

const hcchAnswers = computed(() => data.value?.relations.hcchAnswers ?? []);
</script>
