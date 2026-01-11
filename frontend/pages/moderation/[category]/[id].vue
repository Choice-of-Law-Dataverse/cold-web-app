<template>
  <div class="mx-auto max-w-container px-6 py-12">
    <div class="mb-8">
      <h1 class="text-3xl font-bold">
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
      <UCard class="mb-6" :ui="{ body: { padding: '' } }">
        <template #header>
          <h2 class="text-xl font-semibold">Submission Information</h2>
        </template>

        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow
            v-if="
              suggestion.username ||
              suggestion.user_email ||
              suggestion.token_sub
            "
            label="Submitted by"
          >
            {{
              suggestion.username ||
              suggestion.user_email ||
              suggestion.token_sub ||
              "Unknown"
            }}
          </DetailRow>
          <DetailRow v-if="suggestion.created_at" label="Created">
            {{ formatDate(suggestion.created_at) }}
          </DetailRow>
          <DetailRow v-if="suggestion.source" label="Source">
            {{ suggestion.source }}
          </DetailRow>
          <DetailRow label="ID">
            {{ suggestion.id }}
          </DetailRow>
        </div>
      </UCard>

      <!-- Data fields card -->
      <UCard class="mb-6" :ui="{ body: { padding: '' } }">
        <template #header>
          <h2 class="text-xl font-semibold">Submitted Data</h2>
        </template>

        <div class="flex flex-col gap-4 px-6 py-8">
          <DetailRow
            v-for="(value, key) in filteredPayload"
            :key="key"
            :label="formatFieldName(key)"
          >
            <template v-if="isLongText(value)">
              <p class="prose mt-0 whitespace-pre-wrap">
                {{ formatValue(value) }}
              </p>
            </template>
            <template v-else>
              <p class="prose mt-0">{{ formatValue(value) }}</p>
            </template>
          </DetailRow>
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
import { useModerationApi } from "@/composables/useModerationApi";
import DetailRow from "@/components/ui/DetailRow.vue";

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
  const metaFields = new Set([
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
    "full_text",
    "pdf_uuid",
    "pdf_url",
    "analysis_done",
    "analysis_ready",
    "workflow_started",
    "parallel_execution_started",
    // New format internal fields
    "raw_data",
    "draft_id",
    "notes",
    "correlation_id",
  ]);

  const filtered: Record<string, unknown> = {};
  const payload = suggestion.value.payload;

  // For case analyzer, collect fields with _edited versions (legacy format)
  const editedFields = new Set<string>();
  if (category.value === "case-analyzer") {
    for (const key of Object.keys(payload)) {
      if (key.endsWith("_edited")) {
        const baseField = key.replace("_edited", "");
        editedFields.add(baseField);
      }
    }
  }

  for (const [key, value] of Object.entries(payload)) {
    // Skip if null, empty, or in metadata fields
    if (metaFields.has(key) || value === null || value === "") {
      continue;
    }

    // Case analyzer specific filtering
    if (category.value === "case-analyzer") {
      // Skip *_printed, *_reasoning, and *_confidence fields
      if (
        key.endsWith("_printed") ||
        key.endsWith("_reasoning") ||
        key.endsWith("_confidence")
      ) {
        continue;
      }

      // Skip full_text
      if (key === "full_text") {
        continue;
      }

      // Skip base field if _edited version exists (legacy format)
      if (editedFields.has(key)) {
        continue;
      }
    }

    filtered[key] = value;
  }

  return filtered;
});

const formatFieldName = (key: string): string => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
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
    const result = await approveSuggestion(category.value, suggestionId.value);
    successMessage.value =
      result.message || "Suggestion approved successfully!";
    showSuccessModal.value = true;
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : "Failed to approve suggestion";
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
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : "Failed to reject suggestion";
    showErrorModal.value = true;
  } finally {
    rejecting.value = false;
  }
};

const goToList = () => {
  navigateTo(`/moderation/${category.value}`);
};
</script>
