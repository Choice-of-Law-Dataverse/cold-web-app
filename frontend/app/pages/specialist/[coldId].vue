<template>
  <div>
    <h1 v-if="specialist?.specialist" class="sr-only">
      {{ specialist.specialist }}
    </h1>
    <BaseDetailLayout
      table="Specialists"
      :loading="loading"
      :error="error"
      :data="specialist || {}"
      :labels="specialistLabels"
      :show-suggest-edit="true"
    >
      <template #website="{ value }">
        <DetailRow :label="specialistLabels.website">
          <a
            :href="String(value)"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary break-all hover:underline"
          >
            {{ value }}
          </a>
        </DetailRow>
      </template>

      <template #search-links>
        <DetailRow label="Jurisdictions" variant="jurisdiction">
          <RelatedItemsList :items="jurisdictions" base-path="/jurisdiction" />
        </DetailRow>
        <DetailRow label="International Instruments" variant="instrument">
          <RelatedItemsList
            :items="internationalInstruments"
            base-path="/international-instrument"
          />
        </DetailRow>
        <DetailRow label="Related Literature" variant="literature">
          <RelatedItemsList :items="literature" base-path="/literature" />
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="specialist?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[specialist?.specialist]"
      fallback="Specialist"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useSpecialistDetail } from "@/composables/useRecordDetails";
import { specialistLabels } from "@/config/labels";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const specialistId = ref(route.params.coldId as string);

const {
  data: specialist,
  isLoading: loading,
  error,
} = useSpecialistDetail(specialistId);

const jurisdictions = computed<RelatedItem[]>(() =>
  (specialist.value?.relations.jurisdictions ?? []).map((j) => ({
    id: j.coldId || String(j.id),
    title: j.name || String(j.id),
  })),
);

const internationalInstruments = computed<RelatedItem[]>(() =>
  (specialist.value?.relations.internationalInstruments ?? []).map((ii) => ({
    id: ii.coldId || String(ii.id),
    title: ii.name || String(ii.id),
  })),
);

const literature = computed<RelatedItem[]>(() =>
  (specialist.value?.relations.literature ?? []).map((lit) => ({
    id: lit.coldId || String(lit.id),
    title: lit.title || String(lit.id),
  })),
);
</script>
