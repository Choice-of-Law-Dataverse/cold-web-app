<template>
  <div>
    <h1 v-if="arbitralRule?.setOfRules" class="sr-only">
      {{ arbitralRule.setOfRules }}
    </h1>
    <BaseDetailLayout
      table="Arbitral Rules"
      :loading="loading"
      :error="error"
      :data="arbitralRule || {}"
      :labels="arbitralRuleLabels"
      :relations="arbitralRule?.relations"
      :show-suggest-edit="true"
    >
      <template #footer>
        <LastModified :date="arbitralRule?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[arbitralRule?.setOfRules]"
      fallback="Arbitral Rule"
    />

    <EntityFeedback
      entity-type="arbitral_rule"
      :entity-id="ruleId"
      :entity-title="arbitralRule?.setOfRules as string"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import { useArbitralRule } from "@/composables/useRecordDetails";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { arbitralRuleLabels } from "@/config/labels";

const route = useRoute();

const ruleId = ref(route.params.coldId as string);

const {
  data: arbitralRule,
  isLoading: loading,
  error,
} = useArbitralRule(ruleId);
</script>
