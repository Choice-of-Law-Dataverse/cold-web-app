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
          :jurisdiction-code="
            (primaryJurisdiction?.coldId as string) ?? undefined
          "
          :jurisdiction-name="
            (primaryJurisdiction?.name as string) ?? undefined
          "
        />
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.titleInEnglish as string]"
      fallback="Domestic Instrument"
    />

    <EntityFeedback
      entity-type="domestic_instrument"
      :entity-id="instrumentId"
      :entity-title="data?.titleInEnglish as string"
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

const instrumentId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/domestic-instrument",
  instrumentId,
);

const primaryJurisdiction = computed(() => {
  const rels = data.value?.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  return rels?.jurisdictions?.[0] ?? null;
});
</script>
