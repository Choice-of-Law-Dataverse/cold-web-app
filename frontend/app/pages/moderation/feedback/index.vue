<template>
  <div class="py-12">
    <div class="mb-8">
      <h1 class="text-3xl font-bold">Pending: Entity Feedback</h1>
    </div>

    <div v-if="pending" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin" />
    </div>

    <UAlert
      v-else-if="error"
      color="error"
      variant="subtle"
      title="Error"
      :description="error.message"
      class="mb-4"
    />

    <div
      v-else-if="!feedbackItems || feedbackItems.length === 0"
      class="py-12 text-center"
    >
      <p class="text-gray-600">No pending feedback.</p>
    </div>

    <div v-else class="space-y-4">
      <UCard
        v-for="item in feedbackItems"
        :key="item.id"
        class="cold-ucard-no-padding cursor-pointer transition-shadow hover:shadow-lg"
        @click="navigateTo(`/moderation/feedback/${item.id}`)"
      >
        <template #header>
          <div class="flex items-start justify-between px-6 py-4">
            <div class="flex-1">
              <h3 class="text-lg font-semibold">
                {{ item.entity_title || `Entity #${item.entity_id}` }}
              </h3>
              <p class="mt-1 text-sm text-gray-600">
                {{ item.submitter_email }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <UBadge color="primary" variant="subtle">
                {{ entityTypeLabel(item.entity_type) }}
              </UBadge>
              <UBadge color="info" variant="subtle">
                {{ feedbackTypeLabel(item.feedback_type) }}
              </UBadge>
            </div>
          </div>
        </template>

        <div class="flex flex-col gap-3 px-6 py-4">
          <p class="text-sm text-gray-700">
            {{ truncate(item.message, 200) }}
          </p>
          <p v-if="item.created_at" class="text-xs text-gray-500">
            {{ formatDateLong(item.created_at) }}
          </p>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDateLong } from "@/utils/format";

definePageMeta({
  middleware: ["moderation"],
});

interface FeedbackItem {
  id: number;
  created_at: string;
  entity_type: string;
  entity_id: string;
  entity_title: string | null;
  feedback_type: string;
  message: string;
  submitter_email: string;
  moderation_status: string;
}

const ENTITY_TYPE_LABELS: Record<string, string> = {
  court_decision: "Court Decision",
  domestic_instrument: "Domestic Instrument",
  regional_instrument: "Regional Instrument",
  international_instrument: "International Instrument",
  literature: "Literature",
  arbitral_award: "Arbitral Award",
  arbitral_rule: "Arbitral Rule",
  question: "Question",
  jurisdiction: "Jurisdiction",
};

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  improve: "Suggest Improvement",
  missing_data: "Missing Data",
  wrong_info: "Wrong Information",
  outdated: "Outdated",
  other: "Other",
};

function entityTypeLabel(type: string): string {
  return ENTITY_TYPE_LABELS[type] || type;
}

function feedbackTypeLabel(type: string): string {
  return FEEDBACK_TYPE_LABELS[type] || type;
}

function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + "...";
}

const {
  data: feedbackItems,
  pending,
  error,
} = await useFetch<FeedbackItem[]>("/api/proxy/feedback/pending", {
  method: "GET",
});
</script>
