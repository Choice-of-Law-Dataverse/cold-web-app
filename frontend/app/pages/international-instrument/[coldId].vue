<template>
  <div>
    <h1 v-if="data?.name" class="sr-only">
      {{ data.name }}
    </h1>
    <BaseDetailLayout
      table="International Instruments"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <InternationalInstrumentContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.name as string]"
      fallback="International Instrument"
    />

    <EntityFeedback
      entity-type="international_instrument"
      :entity-id="instrumentId"
      :entity-title="(data?.name as string) || undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InternationalInstrumentContent from "@/components/entity/content/InternationalInstrumentContent.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/international-instrument",
  instrumentId,
);
</script>
