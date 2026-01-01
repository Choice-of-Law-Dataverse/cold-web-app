<template>
  <div class="container mx-auto max-w-6xl px-6 py-12">
    <div class="mb-8 flex items-center justify-between">
      <div>
        <UButton
          variant="ghost"
          icon="i-heroicons-arrow-left"
          @click="navigateTo('/moderation')"
        >
          Back to Categories
        </UButton>
        <h1 class="mt-4 text-3xl font-bold">
          Pending: {{ categoryLabel }}
        </h1>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="pending" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin" />
    </div>

    <!-- Error state -->
    <UAlert
      v-else-if="error"
      color="red"
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
      <p class="text-gray-600">No pending suggestions.</p>
    </div>

    <!-- Suggestions list -->
    <div v-else class="space-y-4">
      <UCard
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="cold-ucard cursor-pointer transition-shadow hover:shadow-lg"
        @click="navigateTo(`/moderation/${category}/${suggestion.id}`)"
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
            <UBadge color="blue" variant="subtle"> Pending </UBadge>
          </div>
        </template>

        <div class="flex flex-col gap-3 px-6 py-4">
          <DetailRow
            v-if="suggestion.username || suggestion.user_email"
            label="Submitted by"
          >
            <p class="prose mt-0 text-sm">
              {{ suggestion.username || suggestion.user_email || "Unknown" }}
            </p>
          </DetailRow>
          <DetailRow v-if="suggestion.created_at" label="Created">
            <p class="prose mt-0 text-sm">
              {{ formatDate(suggestion.created_at) }}
            </p>
          </DetailRow>
          <DetailRow v-if="suggestion.source" label="Source">
            <p class="prose mt-0 text-sm">{{ suggestion.source }}</p>
          </DetailRow>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import { getCategoryLabel } from "@/config/moderationConfig";
import type { PendingSuggestion } from "@/composables/useModerationApi";
import DetailRow from "@/components/ui/DetailRow.vue";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const category = computed(() => route.params.category as string);
const categoryLabel = computed(() => getCategoryLabel(category.value));

const { listPendingSuggestions } = useModerationApi();

const {
  data: suggestions,
  pending,
  error,
  refresh,
} = await useAsyncData(
  `pending-${category.value}`,
  () => listPendingSuggestions(category.value),
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
      return payload[field];
    }
  }

  return `Entry #${suggestion.id}`;
};

const getSuggestionMeta = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const parts: string[] = [];

  // Add jurisdiction if available
  if (payload.jurisdiction || payload.country) {
    parts.push(`Jurisdiction: ${payload.jurisdiction || payload.country}`);
  }

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

const formatDate = (dateString: string): string => {
  try {
    return format(new Date(dateString), "PPP");
  } catch {
    return dateString;
  }
};
</script>

<style scoped>
.cold-ucard :deep(.px-4) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.cold-ucard :deep(.py-5) {
  padding-top: 16px !important;
  padding-bottom: 18px !important;
}

.cold-ucard :deep(.sm\:px-6) {
  padding-left: 16px !important;
  padding-right: 16px !important;
}
</style>
