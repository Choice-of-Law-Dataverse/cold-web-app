<template>
  <div>
    <BaseDetailLayout
      table="Arbitral Rules"
      :page-heading="data?.setOfRules ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="arbitral_rule"
      :entity-id="coldId"
      :entity-title="data?.setOfRules ?? undefined"
    >
      <EntityContent v-if="data" base-path="/arbitral-rule" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.setOfRules]"
      fallback="Arbitral Rule"
      :description-candidates="descriptionCandidates"
      :breadcrumbs="breadcrumbs"
      :json-ld="jsonLd"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildArbitralRuleNode } from "@/utils/structuredData";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/arbitral-rule", coldId);

const descriptionCandidates = computed(() => [
  data.value?.setOfRules,
  data.value?.inForceFrom ? `In force from ${data.value.inForceFrom}` : null,
  "Set of arbitral rules and its choice of law provisions, recorded in the Choice of Law Dataverse.",
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Arbitral Rules", path: "/arbitral-rule" },
  {
    name: data.value?.setOfRules ?? "Arbitral Rule",
    path: `/arbitral-rule/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildArbitralRuleNode(siteUrl, path, data.value) : null;
</script>
