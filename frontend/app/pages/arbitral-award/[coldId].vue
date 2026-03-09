<template>
  <div>
    <h1 v-if="data?.caseNumber" class="sr-only">
      Arbitral Award: {{ data.caseNumber }}
    </h1>
    <BaseDetailLayout
      table="Arbitral Awards"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :formatted-jurisdiction="
        (data?.formattedJurisdictions as { name: string }[])?.map(
          (j) => j.name,
        ) || []
      "
      :formatted-theme="
        (data?.formattedThemes as { theme: string }[])?.map((t) => t.theme) ||
        []
      "
      :show-suggest-edit="true"
    >
      <EntityContent base-path="/arbitral-award" :data="data || {}" />

      <template #footer>
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[caseNumberTitle]"
      fallback="Arbitral Award"
    />

    <EntityFeedback
      entity-type="arbitral_award"
      :entity-id="awardId"
      :entity-title="caseNumberTitle ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";

const route = useRoute();

const awardId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/arbitral-award", awardId);

const caseNumberTitle = computed(() => {
  const cn = data.value?.caseNumber as string | undefined;
  return cn?.trim() ? `Case Number ${cn}` : null;
});
</script>
