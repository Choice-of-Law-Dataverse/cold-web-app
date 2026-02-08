<template>
  <div>
    <BaseDetailLayout
      table="Arbitral Rules"
      :loading="loading"
      :error="error"
      :data="arbitralRule || {}"
      :labels="arbitralRuleLabels"
      :show-suggest-edit="true"
    >
      <template #footer>
        <LastModified :date="arbitralRule?.['Last Modified']" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[arbitralRule?.['Set of Rules']]"
      fallback="Arbitral Rule"
    />

    <EntityFeedback
      entity-type="arbitral_rule"
      :entity-id="ruleId"
      :entity-title="arbitralRule?.['Set of Rules'] as string"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useArbitralRule } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { arbitralRuleLabels } from "@/config/labels";

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const ruleId = ref(route.params.id as string);

const {
  data: arbitralRule,
  isLoading: loading,
  error,
} = useArbitralRule(ruleId);
</script>
