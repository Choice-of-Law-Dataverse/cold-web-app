<template>
  <div>
    <BaseDetailLayout
      table="Jurisdictions"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :formatted-jurisdiction="[data?.name ?? '']"
      :show-suggest-edit="true"
    >
      <DetailRow label="">
        <h1 class="mb-4 text-3xl font-semibold md:text-4xl">
          Country Report for {{ data?.name || "N/A" }}
        </h1>
      </DetailRow>

      <EntityContent base-path="/jurisdiction" :data="data || {}" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>
    <ClientOnly>
      <div class="mt-8">
        <JurisdictionComparisonTable
          v-if="jurisdictionOption"
          :primary-jurisdiction="jurisdictionOption"
        />
      </div>
      <template #fallback>
        <div class="mt-8 px-6">
          <div class="max-w-container mx-auto w-full">
            <div class="col-span-12">
              <UCard
                :ui="{
                  body: '!p-0',
                  header: 'border-b-0 px-4 py-5 sm:px-6',
                }"
              >
                <template #header>
                  <div class="flex justify-between">
                    <h3 class="comparison-title mb-4">Comparison</h3>
                    <span class="mb-4 flex flex-wrap gap-2">
                      <UButton
                        to="/learn/methodology"
                        color="primary"
                        variant="ghost"
                        size="xs"
                        leading-icon="i-material-symbols:school-outline"
                        trailing-icon="i-material-symbols:arrow-forward"
                      >
                        Methodology
                      </UButton>
                      <UButton
                        to="/learn/glossary"
                        color="primary"
                        variant="ghost"
                        size="xs"
                        leading-icon="i-material-symbols:dictionary-outline"
                        trailing-icon="i-material-symbols:arrow-forward"
                      >
                        Glossary
                      </UButton>
                    </span>
                  </div>
                </template>
                <div class="gradient-top-border" />
                <div class="px-4 py-5 sm:px-6">
                  <div class="flex flex-col space-y-3 py-8">
                    <LoadingBar />
                    <LoadingBar />
                    <LoadingBar />
                  </div>
                </div>
              </UCard>
            </div>
          </div>
        </div>
      </template>
    </ClientOnly>

    <PageSeoMeta :title-candidates="[data?.name]" fallback="Country Report" />

    <EntityFeedback
      entity-type="jurisdiction"
      :entity-id="jurisdictionId"
      :entity-title="data?.name ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import JurisdictionComparisonTable from "@/components/jurisdiction/JurisdictionComparisonTable.vue";
import LastModified from "@/components/ui/LastModified.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const jurisdictionId = ref((route.params.coldId as string).toUpperCase());

const { data, isLoading, error } = useEntityData(
  "/jurisdiction",
  jurisdictionId,
);

const jurisdictionOption = computed(() => {
  if (!data.value) return null;
  return {
    name: data.value.name || "",
    label: data.value.name || "",
    coldId: data.value.coldId || "",
  };
});
</script>
