<template>
  <div class="py-12">
    <div class="mb-8 flex items-center gap-3">
      <NuxtLink
        to="/moderation"
        class="border-cold-gray text-cold-slate hover:border-cold-purple hover:text-cold-purple flex h-8 w-8 items-center justify-center rounded-lg border transition-colors"
      >
        <UIcon name="i-heroicons-arrow-left-16-solid" class="h-4 w-4" />
      </NuxtLink>
      <div>
        <h1 class="text-cold-night text-2xl font-bold tracking-tight">
          Entity Feedback
        </h1>
        <p class="text-cold-slate text-sm">
          Pending review
          <template v-if="feedbackItems">
            &middot; {{ feedbackItems.length }}
            {{ feedbackItems.length === 1 ? "item" : "items" }}
          </template>
        </p>
      </div>
    </div>

    <div v-if="pending" class="flex justify-center py-16">
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
      class="empty-state"
    >
      <UIcon
        name="i-heroicons-check-circle"
        class="text-cold-green mx-auto h-12 w-12"
      />
      <p class="text-cold-night mt-3 font-medium">Queue is clear</p>
      <p class="text-cold-slate mt-1 text-sm">No feedback pending review.</p>
    </div>

    <div v-else class="feedback-list">
      <div
        v-for="item in feedbackItems"
        :key="item.id"
        class="feedback-row"
        @click="navigateTo(`/moderation/feedback/${item.id}`)"
      >
        <div class="flex min-w-0 flex-1 items-start gap-4">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <h3 class="text-cold-night truncate text-sm font-semibold">
                {{ item.entityTitle || `Entity #${item.entityId}` }}
              </h3>
              <UBadge color="primary" variant="subtle" size="xs">
                {{ entityTypeLabel(item.entityType) }}
              </UBadge>
              <UBadge color="info" variant="subtle" size="xs">
                {{ feedbackTypeLabel(item.feedbackType) }}
              </UBadge>
            </div>

            <p class="text-cold-slate mt-1.5 line-clamp-2 text-xs">
              {{ item.message }}
            </p>

            <div class="mt-2 flex items-center gap-3">
              <span class="meta-item">
                <UIcon
                  name="i-heroicons-envelope-16-solid"
                  class="h-3.5 w-3.5"
                />
                {{ item.submitterEmail }}
              </span>
              <span v-if="item.createdAt" class="meta-item">
                <UIcon
                  name="i-heroicons-calendar-16-solid"
                  class="h-3.5 w-3.5"
                />
                {{ formatDateLong(item.createdAt) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDateLong } from "@/utils/format";
import { entityTypeLabel, feedbackTypeLabel } from "@/config/feedback";
import { useFeedbackModeration } from "@/composables/useFeedbackModeration";

definePageMeta({
  middleware: ["moderation"],
});

const { listPending } = useFeedbackModeration();

const {
  data: feedbackItems,
  pending,
  error,
} = await useAsyncData("feedback-pending", () => listPending(), {
  server: false,
});
</script>

<style scoped>
h1,
h2,
h3 {
  font-family: "DM Sans", sans-serif;
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  border: 1px dashed var(--color-cold-gray);
  border-radius: 12px;
  background: var(--gradient-subtle);
}

.feedback-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-cold-gray);
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.feedback-row {
  display: flex;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-cold-gray);
  cursor: pointer;
  transition: background 0.15s ease;
}

.feedback-row:last-child {
  border-bottom: none;
}

.feedback-row:hover {
  background: var(--gradient-subtle);
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-cold-slate);
}
</style>
