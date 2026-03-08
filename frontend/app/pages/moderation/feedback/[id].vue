<template>
  <div class="py-12">
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

    <template v-else-if="feedback">
      <div class="mb-8 flex items-center justify-between">
        <h1 class="text-3xl font-bold">Feedback #{{ feedbackId }}</h1>
        <UBadge
          :color="getStatusBadgeColor(feedback.moderationStatus)"
          variant="subtle"
          size="lg"
        >
          {{ getStatusLabel(feedback.moderationStatus) }}
        </UBadge>
      </div>

      <UCard class="mb-6" :ui="{ body: 'p-0' }">
        <template #header>
          <h2 class="px-6 py-4 text-xl font-semibold">Entity</h2>
        </template>
        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow label="Type">
            <p class="result-value-small">
              {{ entityTypeLabel(feedback.entityType) }}
            </p>
          </DetailRow>
          <DetailRow label="Title">
            <NuxtLink
              :to="`/${feedback.entityType.replace(/_/g, '-')}/${feedback.entityId}`"
              class="text-cold-purple hover:underline"
            >
              {{ feedback.entityTitle || feedback.entityId }}
            </NuxtLink>
          </DetailRow>
        </div>
      </UCard>

      <UCard class="mb-6" :ui="{ body: 'p-0' }">
        <template #header>
          <h2 class="px-6 py-4 text-xl font-semibold">Feedback</h2>
        </template>
        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow label="Type">
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

      <div
        v-if="feedback.moderationStatus === 'pending'"
        class="flex items-center gap-4"
      >
        <UButton
          color="success"
          size="lg"
          :loading="updating"
          @click="handleStatus('reviewed')"
        >
          Mark as Reviewed
        </UButton>
        <UButton
          color="neutral"
          size="lg"
          variant="outline"
          :loading="updating"
          @click="handleStatus('dismissed')"
        >
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
} = await useAsyncData(`feedback-${feedbackId.value}`, () =>
  getDetail(feedbackId.value),
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
