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
      <template #title-actions>
        <template v-if="data">
          <PdfLink
            :pdf-field="data.attachment"
            :record-id="String(data.coldId || '')"
            folder-name="international-instruments"
          />
          <SourceExternalLink :source-url="data.displayUrl" />
        </template>
      </template>

      <InternationalInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <div v-if="hcchAnswers.length" class="mt-8">
      <HcchAnswersList :answers="hcchAnswers" />
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
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import HcchAnswersList from "@/components/ui/HcchAnswersList.vue";
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

const hcchAnswers = computed(() =>
  (data.value?.relations.hcchAnswers ?? [])
    .filter((a) => a.adaptedQuestion || a.position)
    .sort((a, b) =>
      (a.coldId ?? "").localeCompare(b.coldId ?? "", undefined, {
        numeric: true,
      }),
    ),
);
</script>
