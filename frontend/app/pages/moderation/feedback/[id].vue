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
          :color="getStatusBadgeColor(feedback.moderation_status)"
          variant="subtle"
          size="lg"
        >
          {{ getStatusLabel(feedback.moderation_status) }}
        </UBadge>
      </div>

      <UCard class="cold-ucard-no-padding mb-6">
        <template #header>
          <h2 class="px-6 py-4 text-xl font-semibold">Entity</h2>
        </template>
        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow label="Type">
            <p class="result-value-small">
              {{ entityTypeLabel(feedback.entity_type) }}
            </p>
          </DetailRow>
          <DetailRow label="Title">
            <NuxtLink
              :to="`/${feedback.entity_type.replace(/_/g, '-')}/${feedback.entity_id}`"
              class="text-cold-purple hover:underline"
            >
              {{ feedback.entity_title || feedback.entity_id }}
            </NuxtLink>
          </DetailRow>
        </div>
      </UCard>

      <UCard class="cold-ucard-no-padding mb-6">
        <template #header>
          <h2 class="px-6 py-4 text-xl font-semibold">Feedback</h2>
        </template>
        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow label="Type">
            <UBadge color="info" variant="subtle">
              {{ feedbackTypeLabel(feedback.feedback_type) }}
            </UBadge>
          </DetailRow>
          <DetailRow label="Message">
            <p class="result-value-small whitespace-pre-line">
              {{ feedback.message }}
            </p>
          </DetailRow>
          <DetailRow label="Submitter">
            <p class="result-value-small">{{ feedback.submitter_email }}</p>
          </DetailRow>
          <DetailRow v-if="feedback.created_at" label="Submitted">
            <p class="result-value-small">
              {{ formatDateLong(feedback.created_at) }}
            </p>
          </DetailRow>
        </div>
      </UCard>

      <div
        v-if="feedback.moderation_status === 'pending'"
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

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const toast = useToast();
const feedbackId = computed(() => Number(route.params.id));

interface FeedbackDetail {
  id: number;
  created_at: string;
  entity_type: string;
  entity_id: string;
  entity_title: string | null;
  feedback_type: string;
  message: string;
  submitter_email: string;
  token_sub: string | null;
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

const {
  data: feedback,
  pending,
  error,
} = await useFetch<FeedbackDetail>(`/api/proxy/feedback/${feedbackId.value}`, {
  method: "GET",
});

const updating = ref(false);

async function handleStatus(status: "reviewed" | "dismissed") {
  updating.value = true;
  try {
    await $fetch(`/api/proxy/feedback/${feedbackId.value}`, {
      method: "PATCH",
      body: { moderation_status: status },
    });
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
