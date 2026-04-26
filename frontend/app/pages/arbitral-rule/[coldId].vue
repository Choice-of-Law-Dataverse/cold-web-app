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
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/arbitral-rule", coldId);
</script>
