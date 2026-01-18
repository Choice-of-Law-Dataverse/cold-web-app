<template>
  <div>
    <BaseDetailLayout
      table="Arbitral Awards"
      :loading="loading"
      :data="arbitralAward || {}"
      :labels="arbitralAwardLabels"
      :formatted-jurisdiction="arbitralAward?.formattedJurisdictions || []"
      :formatted-theme="arbitralAward?.formattedThemes || []"
      :show-suggest-edit="true"
    >
      <template #footer>
        <LastModified :date="arbitralAward?.['Last Modified']" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        arbitralAward?.['Case Number'] &&
        String(arbitralAward['Case Number']).trim()
          ? `Case Number ${arbitralAward['Case Number']}`
          : null,
      ]"
      fallback="Arbitral Award"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useArbitralAward } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { arbitralAwardLabels } from "@/config/labels";

const route = useRoute();

const { data: arbitralAward, isLoading: loading } = useArbitralAward(
  computed(() => route.params.id as string),
);
</script>
