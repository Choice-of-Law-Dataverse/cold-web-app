<template>
  <div class="py-12">
    <PageHero
      title="My Case Analyses"
      subtitle="View the status of your submitted case analyses"
      class="mb-8"
    />

    <!-- Loading state -->
    <div v-if="pending" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin" />
    </div>

    <!-- Error state -->
    <UAlert
      v-else-if="error"
      color="error"
      variant="subtle"
      title="Error"
      :description="error.message"
      class="mb-4"
    />

    <!-- Empty state -->
    <div
      v-else-if="!analyses || analyses.length === 0"
      class="py-12 text-center"
    >
      <UIcon
        name="i-heroicons-document-text"
        class="mx-auto mb-4 h-12 w-12 text-gray-400"
      />
      <p class="text-gray-600">You haven't started any case analyses yet.</p>
      <AppButtonGradient
        class="mt-4"
        to="/court-decision/new"
        icon="i-heroicons-plus"
      >
        Start New Analysis
      </AppButtonGradient>
    </div>

    <!-- Analyses list -->
    <div v-else>
      <div class="mb-4 flex items-center justify-between">
        <p class="text-sm text-gray-600">
          {{ analyses.length }} analys{{ analyses.length !== 1 ? "es" : "is" }}
        </p>
        <UButton
          variant="ghost"
          color="primary"
          to="/court-decision/new"
          icon="i-heroicons-plus"
          size="sm"
        >
          New Analysis
        </UButton>
      </div>

      <UCard :ui="{ body: 'p-0' }">
        <table class="w-full">
          <caption class="sr-only">
            Submitted case analyses with date, citation, status, and action
          </caption>
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th
                scope="col"
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Date
              </th>
              <th
                scope="col"
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Case Citation
              </th>
              <th
                scope="col"
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Status
              </th>
              <th
                scope="col"
                class="px-4 py-3 text-right text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="analysis in analyses"
              :key="analysis.id"
              class="border-b border-gray-100 last:border-b-0 dark:border-gray-800"
            >
              <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                {{ formatDateShort(analysis.createdAt) }}
              </td>
              <td class="px-4 py-3">
                <span
                  v-if="analysis.caseCitation"
                  class="text-sm font-medium text-gray-900 dark:text-gray-100"
                >
                  {{ analysis.caseCitation }}
                </span>
                <span
                  v-else-if="analysis.fileName"
                  class="text-sm text-gray-600 dark:text-gray-400"
                >
                  {{ analysis.fileName }}
                </span>
                <span v-else class="text-sm text-gray-400 italic">
                  No citation yet
                </span>
              </td>
              <td class="px-4 py-3">
                <UBadge
                  :color="getStatusBadgeColor(analysis.moderationStatus)"
                  variant="subtle"
                  size="sm"
                >
                  {{ getStatusLabelForUser(analysis.moderationStatus) }}
                </UBadge>
              </td>
              <td class="px-4 py-3 text-right">
                <UButton
                  v-if="canRecoverAnalysis(analysis.moderationStatus)"
                  variant="outline"
                  color="neutral"
                  size="xs"
                  :to="`/court-decision/new?draft=${analysis.id}`"
                >
                  {{
                    analysis.moderationStatus === "failed" ? "Retry" : "Resume"
                  }}
                </UButton>
                <span
                  v-else
                  class="text-xs text-gray-400"
                  :aria-label="
                    analysis.moderationStatus === 'approved'
                      ? 'Analysis has been approved'
                      : analysis.moderationStatus === 'rejected'
                        ? 'Analysis was rejected'
                        : 'Awaiting moderation'
                  "
                >
                  {{ getAnalysisActionText(analysis.moderationStatus) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  getStatusBadgeColor,
  getStatusLabelForUser,
  canRecoverAnalysis,
  getAnalysisActionText,
} from "@/utils/moderationStatus";
import { formatDateShort } from "@/utils/format";
import { useApiClient } from "@/composables/useApiClient";
import PageHero from "@/components/ui/PageHero.vue";

definePageMeta({
  middleware: ["auth"],
});

const { client } = useApiClient();

const {
  data: analyses,
  pending,
  error,
} = await useAsyncData(
  "my-analyses",
  async () => {
    const { data, error } = await client.GET("/case-analyzer/my-analyses");
    if (error) throw error;
    return data;
  },
  { server: false },
);
</script>
