<template>
  <div class="container mx-auto max-w-4xl px-6 py-12">
    <div class="mb-8">
      <UButton
        variant="ghost"
        icon="i-heroicons-arrow-left"
        @click="navigateTo(`/moderation/${category}`)"
      >
        Back to List
      </UButton>
      <h1 class="mt-4 text-3xl font-bold">
        {{ categoryLabel }} — Entry #{{ suggestionId }}
      </h1>
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

    <!-- Suggestion detail -->
    <div v-else-if="suggestion">
      <!-- Metadata card -->
      <UCard class="mb-6">
        <template #header>
          <h2 class="text-xl font-semibold">Submission Information</h2>
        </template>

        <div class="space-y-3">
          <div v-if="suggestion.username || suggestion.user_email">
            <strong class="text-gray-700">Submitted by:</strong>
            <span class="ml-2">{{
              suggestion.username || suggestion.user_email || "Unknown"
            }}</span>
          </div>
          <div v-if="suggestion.created_at">
            <strong class="text-gray-700">Created:</strong>
            <span class="ml-2">{{ formatDate(suggestion.created_at) }}</span>
          </div>
          <div v-if="suggestion.source">
            <strong class="text-gray-700">Source:</strong>
            <span class="ml-2">{{ suggestion.source }}</span>
          </div>
          <div>
            <strong class="text-gray-700">ID:</strong>
            <span class="ml-2">{{ suggestion.id }}</span>
          </div>
        </div>
      </UCard>

      <!-- Data fields card -->
      <UCard class="mb-6">
        <template #header>
          <h2 class="text-xl font-semibold">Submitted Data</h2>
        </template>

        <div class="space-y-4">
          <div
            v-for="(value, key) in filteredPayload"
            :key="key"
            class="border-b border-gray-200 pb-3 last:border-0"
          >
            <strong class="block text-sm font-semibold text-gray-700">
              {{ formatFieldName(key) }}
            </strong>
            <div class="mt-1 text-gray-900">
              <template v-if="isLongText(value)">
                <p class="whitespace-pre-wrap">{{ formatValue(value) }}</p>
              </template>
              <template v-else>
                {{ formatValue(value) }}
              </template>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Action buttons -->
      <div class="flex gap-4">
        <UButton
          color="green"
          size="lg"
          :loading="approving"
          :disabled="rejecting"
          @click="handleApprove"
        >
          Approve
        </UButton>
        <UButton
          color="red"
          size="lg"
          variant="outline"
          :loading="rejecting"
          :disabled="approving"
          @click="handleReject"
        >
          Reject
        </UButton>
      </div>
    </div>

    <!-- Success modal -->
    <UModal v-model="showSuccessModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Success</h3>
        </template>
        <p class="text-gray-700">{{ successMessage }}</p>
        <template #footer>
          <div class="flex justify-end">
            <UButton @click="goToList"> Back to List </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- Error modal -->
    <UModal v-model="showErrorModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-red-600">Error</h3>
        </template>
        <p class="text-gray-700">{{ errorMessage }}</p>
        <template #footer>
          <div class="flex justify-end">
            <UButton @click="showErrorModal = false"> Close </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import { getCategoryLabel } from "@/config/moderationConfig";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const category = computed(() => route.params.category as string);
const suggestionId = computed(() => Number(route.params.id));
const categoryLabel = computed(() => getCategoryLabel(category.value));

const { getSuggestionDetail, approveSuggestion, rejectSuggestion } =
  useModerationApi();

const {
  data: suggestion,
  pending,
  error,
} = await useAsyncData(
  `suggestion-${category.value}-${suggestionId.value}`,
  () => getSuggestionDetail(category.value, suggestionId.value),
);

const approving = ref(false);
const rejecting = ref(false);
const showSuccessModal = ref(false);
const showErrorModal = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const filteredPayload = computed(() => {
  if (!suggestion.value?.payload) return {};

  // Filter out metadata fields
  const metaFields = [
    "submitter_email",
    "submitter_comments",
    "official_source_pdf",
    "source_pdf",
    "attachment",
    "category",
    "moderation_status",
    "moderated_by",
    "moderation_note",
    "merged_record_id",
  ];

  const filtered: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(suggestion.value.payload)) {
    if (!metaFields.includes(key) && value !== null && value !== "") {
      filtered[key] = value;
    }
  }

  return filtered;
});

const formatFieldName = (key: string): string => {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
};

const formatValue = (value: unknown): string => {
  if (value === null || value === undefined) return "N/A";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
};

const isLongText = (value: unknown): boolean => {
  if (typeof value !== "string") return false;
  return value.length > 100 || value.includes("\n");
};

const formatDate = (dateString: string): string => {
  try {
    return format(new Date(dateString), "PPP");
  } catch {
    return dateString;
  }
};

const handleApprove = async () => {
  approving.value = true;
  try {
    const result = await approveSuggestion(
      category.value,
      suggestionId.value,
    );
    successMessage.value =
      result.message || "Suggestion approved successfully!";
    showSuccessModal.value = true;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to approve suggestion";
    showErrorModal.value = true;
  } finally {
    approving.value = false;
  }
};

const handleReject = async () => {
  rejecting.value = true;
  try {
    const result = await rejectSuggestion(category.value, suggestionId.value);
    successMessage.value =
      result.message || "Suggestion rejected successfully!";
    showSuccessModal.value = true;
  } catch (err: any) {
    errorMessage.value = err.message || "Failed to reject suggestion";
    showErrorModal.value = true;
  } finally {
    rejecting.value = false;
  }
};

const goToList = () => {
  navigateTo(`/moderation/${category.value}`);
};
</script>
