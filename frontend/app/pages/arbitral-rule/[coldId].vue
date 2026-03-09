<template>
  <div>
    <h1 v-if="data?.setOfRules" class="sr-only">
      {{ data.setOfRules }}
    </h1>
    <BaseDetailLayout
      table="Arbitral Rules"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <EntityContent base-path="/arbitral-rule" :data="data || {}" />

      <template #footer>
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.setOfRules as string]"
      fallback="Arbitral Rule"
    />

    <EntityFeedback
      entity-type="arbitral_rule"
      :entity-id="ruleId"
      :entity-title="data?.setOfRules as string"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";

const route = useRoute();

const ruleId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/arbitral-rule", ruleId);
</script>
