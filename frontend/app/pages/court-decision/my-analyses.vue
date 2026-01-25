<template>
  <div class="py-12">
    <div class="page-hero mb-8">
      <h1 class="page-hero__title">My Case Analyses</h1>
      <p class="page-hero__subtitle">
        View the status of your submitted case analyses
      </p>
    </div>

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
      <UButton
        class="btn-primary-gradient mt-4"
        to="/court-decision/new"
        icon="i-heroicons-plus"
      >
        Start New Analysis
      </UButton>
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

      <UCard class="cold-ucard-no-padding">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Date
              </th>
              <th
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Case Citation
              </th>
              <th
                class="px-4 py-3 text-left text-sm font-medium text-gray-600 dark:text-gray-400"
              >
                Status
              </th>
              <th
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
                {{ formatDateShort(analysis.created_at) }}
              </td>
              <td class="px-4 py-3">
                <span
                  v-if="analysis.case_citation"
                  class="text-sm font-medium text-gray-900 dark:text-gray-100"
                >
                  {{ analysis.case_citation }}
                </span>
                <span
                  v-else-if="analysis.file_name"
                  class="text-sm text-gray-600 dark:text-gray-400"
                >
                  {{ analysis.file_name }}
                </span>
                <span v-else class="text-sm text-gray-400 italic">
                  No citation yet
                </span>
              </td>
              <td class="px-4 py-3">
                <UBadge
                  :color="getStatusBadgeColor(analysis.moderation_status)"
                  variant="subtle"
                  size="sm"
                >
                  {{ getStatusLabelForUser(analysis.moderation_status) }}
                </UBadge>
              </td>
              <td class="px-4 py-3 text-right">
                <UButton
                  v-if="canRecoverAnalysis(analysis.moderation_status)"
                  class="action-button"
                  :to="`/court-decision/new?draft=${analysis.id}`"
                >
                  {{
                    analysis.moderation_status === "failed" ? "Retry" : "Resume"
                  }}
                </UButton>
                <span
                  v-else
                  class="text-xs text-gray-400"
                  :title="
                    analysis.moderation_status === 'approved'
                      ? 'Analysis has been approved'
                      : analysis.moderation_status === 'rejected'
                        ? 'Analysis was rejected'
                        : 'Awaiting moderation'
                  "
                >
                  {{ getAnalysisActionText(analysis.moderation_status) }}
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

definePageMeta({
  middleware: ["auth"],
});

interface CaseAnalysis {
  id: number;
  created_at: string;
  case_citation: string | null;
  file_name: string | null;
  moderation_status: string;
}

const {
  data: analyses,
  pending,
  error,
} = await useFetch<CaseAnalysis[]>("/api/proxy/case-analyzer/my-analyses");
</script>
