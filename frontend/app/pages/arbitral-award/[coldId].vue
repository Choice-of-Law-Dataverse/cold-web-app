<template>
  <div>
    <h1 v-if="data?.caseNumber" class="sr-only">
      Arbitral Award: {{ data.caseNumber }}
    </h1>
    <BaseDetailLayout
      table="Arbitral Awards"
      :loading="isLoading"
      :error="error"
      :data="data"
      :formatted-jurisdiction="jurisdictionNames"
      :formatted-theme="themeNames"
      :show-suggest-edit="true"
      entity-type="arbitral_award"
      :entity-id="coldId"
      :entity-title="caseNumberTitle ?? undefined"
    >
      <EntityContent v-if="data" base-path="/arbitral-award" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[caseNumberTitle]"
      fallback="Arbitral Award"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/arbitral-award", coldId);

const jurisdictionNames = computed(() => {
  const names =
    data.value?.relations.jurisdictions
      .map((j) => j.name)
      .filter((n): n is string => Boolean(n)) ?? [];
  if (names.length !== 1) return [];
  return names;
});

const themeNames = computed(
  () =>
    data.value?.relations.themes
      .map((t) => t.theme)
      .filter((t): t is string => Boolean(t)) ?? [],
);

const caseNumberTitle = computed(() => {
  const cn = data.value?.caseNumber;
  return cn?.trim() ? `Case Number ${cn}` : null;
});
</script>
