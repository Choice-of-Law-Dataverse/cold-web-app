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
        class="cursor-pointer transition-shadow hover:shadow-lg"
        :ui="{ body: 'p-0' }"
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
import { entityTypeLabel, feedbackTypeLabel } from "@/config/feedback";

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
