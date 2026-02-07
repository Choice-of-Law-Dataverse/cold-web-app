<template>
  <div class="py-12">
    <div class="mb-8">
      <h1 class="text-3xl font-bold">
        {{ isCaseAnalyzer ? "All Submissions" : "Pending" }}:
        {{ categoryLabel }}
      </h1>
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
      v-else-if="!suggestions || suggestions.length === 0"
      class="py-12 text-center"
    >
      <p class="text-gray-600">
        {{ isCaseAnalyzer ? "No submissions yet." : "No pending suggestions." }}
      </p>
    </div>

    <!-- Suggestions list -->
    <div v-else class="space-y-4">
      <UCard
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        :class="[
          'transition-shadow',
          isClickable(suggestion)
            ? 'cursor-pointer hover:shadow-lg'
            : 'cursor-not-allowed opacity-60',
        ]"
        :ui="{ body: 'p-0' }"
        @click="handleCardClick(suggestion)"
      >
        <template #header>
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold">
                {{ getSuggestionTitle(suggestion) }}
              </h3>
              <p class="mt-1 text-sm text-gray-600">
                {{ getSuggestionMeta(suggestion) }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <UBadge
                v-if="suggestion.payload?.edit_entity_id"
                color="warning"
                variant="subtle"
              >
                Edit
              </UBadge>
              <UBadge
                :color="getStatusBadgeColor(suggestion.moderation_status)"
                variant="subtle"
              >
                {{ getStatusLabel(suggestion.moderation_status) }}
              </UBadge>
            </div>
          </div>
        </template>

        <div class="flex flex-col gap-3 px-6 py-4">
          <DetailRow
            v-if="getPreciseJurisdiction(suggestion)"
            label="Jurisdiction"
          >
            <p class="result-value-small text-sm">
              {{ getPreciseJurisdiction(suggestion) }}
            </p>
          </DetailRow>

          <DetailRow
            v-if="getJurisdiction(suggestion)"
            label="Jurisdiction Type"
          >
            <p class="result-value-small text-sm">
              {{ getJurisdiction(suggestion) }}
            </p>
          </DetailRow>

          <DetailRow
            v-if="suggestion.username || suggestion.user_email"
            label="Submitted by"
          >
            <p class="result-value-small text-sm">
              {{ suggestion.username || suggestion.user_email || "Unknown" }}
            </p>
          </DetailRow>
          <DetailRow v-if="suggestion.created_at" label="Created">
            <p class="result-value-small text-sm">
              {{ formatDateLong(suggestion.created_at) }}
            </p>
          </DetailRow>

          <DetailRow v-if="suggestion.source" label="Source">
            <p class="result-value-small text-sm">{{ suggestion.source }}</p>
          </DetailRow>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getCategoryLabel } from "@/config/moderationConfig";
import { useModerationApi } from "@/composables/useModerationApi";
import type { PendingSuggestion } from "@/composables/useModerationApi";
import { getStatusBadgeColor, getStatusLabel } from "@/utils/moderationStatus";
import { formatDateLong } from "@/utils/format";
import DetailRow from "@/components/ui/DetailRow.vue";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const category = computed(() => route.params.category as string);
const categoryLabel = computed(() => getCategoryLabel(category.value));
const isCaseAnalyzer = computed(() => category.value === "case-analyzer");

const { listPendingSuggestions } = useModerationApi();

const {
  data: suggestions,
  pending,
  error,
} = await useAsyncData(
  `pending-${category.value}`,
  () => listPendingSuggestions(category.value, isCaseAnalyzer.value),
  {
    watch: [category],
  },
);

const getSuggestionTitle = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};

  // Try various title fields
  const titleFields = [
    "case_citation",
    "case_name",
    "title",
    "name",
    "citation",
  ];

  for (const field of titleFields) {
    if (payload[field]) {
      const value = payload[field];
      // Handle array values by taking first element
      const extracted = Array.isArray(value) ? value[0] : value;
      return String(extracted);
    }
  }

  return `Entry #${suggestion.id}`;
};

const getSuggestionMeta = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const parts: string[] = [];

  // Add date if available
  const dateFields = [
    "date_of_judgment",
    "decision_date",
    "date",
    "year",
    "publication_year",
  ];
  for (const field of dateFields) {
    if (payload[field]) {
      parts.push(`Date: ${payload[field]}`);
      break;
    }
  }

  return parts.join(" | ") || "No additional information";
};

const getJurisdiction = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const value = payload.jurisdiction || payload.country;
  if (!value) return "";
  const extracted = Array.isArray(value) ? value[0] : value;
  return String(extracted);
};

const getPreciseJurisdiction = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const value =
    payload.precise_jurisdiction || payload.precise_jurisdiction_edited;
  if (!value) return "";
  const extracted = Array.isArray(value) ? value[0] : value;
  return String(extracted);
};

const isClickable = (suggestion: PendingSuggestion): boolean => {
  // For case-analyzer, approved and rejected items are not clickable
  if (isCaseAnalyzer.value) {
    const status = suggestion.moderation_status;
    return status !== "approved" && status !== "rejected";
  }
  // For other categories, all items are clickable
  return true;
};

const handleCardClick = (suggestion: PendingSuggestion) => {
  if (isClickable(suggestion)) {
    navigateTo(`/moderation/${category.value}/${suggestion.id}`);
  }
};
</script>
