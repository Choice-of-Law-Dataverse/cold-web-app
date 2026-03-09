<template>
  <div>
    <h1 v-if="data?.titleInEnglish" class="sr-only">
      {{ data.titleInEnglish }}
    </h1>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <DomesticInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="primaryJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="primaryJurisdiction?.name ?? undefined"
        />
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.titleInEnglish]"
      fallback="Domestic Instrument"
    />

    <EntityFeedback
      entity-type="domestic_instrument"
      :entity-id="coldId"
      :entity-title="data?.titleInEnglish ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DomesticInstrumentContent from "@/components/entity/content/DomesticInstrumentContent.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/domestic-instrument",
  coldId,
);

const primaryJurisdiction = computed(
  () => data.value?.relations.jurisdictions[0] ?? null,
);
</script>
