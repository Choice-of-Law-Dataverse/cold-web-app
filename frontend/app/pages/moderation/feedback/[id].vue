<template>
  <div class="py-12">
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

    <template v-else-if="feedback">
      <div class="mb-8 flex items-center gap-3">
        <NuxtLink
          to="/moderation/feedback"
          class="border-cold-gray text-cold-slate hover:border-cold-purple hover:text-cold-purple flex h-8 w-8 items-center justify-center rounded-lg border transition-colors"
        >
          <UIcon name="i-heroicons-arrow-left-16-solid" class="h-4 w-4" />
        </NuxtLink>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-3">
            <h1
              class="text-cold-night truncate text-2xl font-bold tracking-tight"
            >
              Feedback #{{ feedbackId }}
            </h1>
            <UBadge
              :color="getStatusBadgeColor(feedback.moderationStatus)"
              variant="subtle"
            >
              {{ getStatusLabel(feedback.moderationStatus) }}
            </UBadge>
          </div>
        </div>
      </div>

      <UCard
        :ui="{
          body: '!p-0',
          header: 'border-b-0 px-6 py-5',
        }"
        class="mb-8"
      >
        <div class="gradient-top-border" />

        <div class="flex flex-col gap-2 px-4 py-4 sm:px-6 sm:py-6">
          <DetailRow label="Entity Type">
            <p class="result-value-small">
              {{ entityTypeLabel(feedback.entityType) }}
            </p>
          </DetailRow>
          <DetailRow label="Entity">
            <NuxtLink
              :to="`/${feedback.entityType.replace(/_/g, '-')}/${feedback.entityId}`"
              class="text-cold-purple hover:underline"
            >
              {{ feedback.entityTitle || feedback.entityId }}
            </NuxtLink>
          </DetailRow>
          <DetailRow label="Feedback Type">
            <UBadge color="info" variant="subtle">
              {{ feedbackTypeLabel(feedback.feedbackType) }}
            </UBadge>
          </DetailRow>
          <DetailRow label="Message">
            <p class="result-value-small whitespace-pre-line">
              {{ feedback.message }}
            </p>
          </DetailRow>
          <DetailRow label="Submitter">
            <p class="result-value-small">{{ feedback.submitterEmail }}</p>
          </DetailRow>
          <DetailRow v-if="feedback.createdAt" label="Submitted">
            <p class="result-value-small">
              {{ formatDateLong(feedback.createdAt) }}
            </p>
          </DetailRow>
        </div>
      </UCard>

      <div v-if="feedback.moderationStatus === 'pending'" class="action-bar">
        <UButton
          color="success"
          size="lg"
          :loading="updating"
          @click="handleStatus('reviewed')"
        >
          <template #leading>
            <UIcon name="i-heroicons-check-16-solid" class="h-4 w-4" />
          </template>
          Mark as Reviewed
        </UButton>
        <UButton
          color="neutral"
          size="lg"
          variant="subtle"
          :loading="updating"
          @click="handleStatus('dismissed')"
        >
          <template #leading>
            <UIcon name="i-heroicons-x-mark-16-solid" class="h-4 w-4" />
          </template>
          Dismiss
        </UButton>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { getStatusBadgeColor, getStatusLabel } from "@/utils/moderationStatus";
import { formatDateLong } from "@/utils/format";
import DetailRow from "@/components/ui/DetailRow.vue";
import { entityTypeLabel, feedbackTypeLabel } from "@/config/feedback";
import { useFeedbackModeration } from "@/composables/useFeedbackModeration";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const toast = useToast();
const feedbackId = computed(() => Number(route.params.id));

const { getDetail, updateStatus } = useFeedbackModeration();

const {
  data: feedback,
  pending,
  error,
} = await useAsyncData(
  `feedback-${feedbackId.value}`,
  () => getDetail(feedbackId.value),
  { server: false },
);

const updating = ref(false);

async function handleStatus(status: "reviewed" | "dismissed") {
  updating.value = true;
  try {
    await updateStatus(feedbackId.value, status);
    toast.add({
      title: "Updated",
      description: `Feedback marked as ${status}.`,
      color: "success",
      duration: 3000,
    });
    navigateTo("/moderation/feedback");
  } catch (err: unknown) {
    toast.add({
      title: "Error",
      description: err instanceof Error ? err.message : "Failed to update",
      color: "error",
      duration: 3000,
    });
    updating.value = false;
  }
}
</script>

<style scoped>
h1,
h2,
h3 {
  font-family: "DM Sans", sans-serif;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--color-cold-gray);
  border-radius: 12px;
  background: var(--gradient-subtle);
}
</style>
