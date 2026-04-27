<template>
  <div class="py-12">
    <div class="mb-8 flex items-center gap-3">
      <NuxtLink
        :to="`/moderation/${category}`"
        class="border-cold-gray text-cold-slate hover:border-cold-purple hover:text-cold-purple flex h-8 w-8 items-center justify-center rounded-lg border transition-colors"
      >
        <UIcon name="i-heroicons-arrow-left-16-solid" class="h-4 w-4" />
      </NuxtLink>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-3">
          <h1
            class="text-cold-night truncate text-2xl font-bold tracking-tight"
          >
            {{ categoryLabel }} #{{ suggestionId }}
          </h1>
          <UBadge
            v-if="suggestion?.moderationStatus"
            :color="getStatusBadgeColor(suggestion.moderationStatus)"
            variant="subtle"
          >
            {{ getStatusLabel(suggestion.moderationStatus) }}
          </UBadge>
        </div>
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

    <div v-else-if="suggestion">
      <div v-if="isEditSuggestion" class="edit-banner mb-6">
        <div class="flex items-center gap-2">
          <UIcon
            name="i-heroicons-pencil-square-16-solid"
            class="h-4 w-4 shrink-0 text-amber-600"
          />
          <span class="text-cold-night text-sm font-medium">
            Edit of existing record
          </span>
        </div>
        <UButton
          variant="outline"
          color="neutral"
          size="xs"
          leading-icon="i-heroicons-eye-16-solid"
          trailing-icon="i-heroicons-eye-16-solid"
          @click="openOriginalEntity"
        >
          View original
        </UButton>
      </div>

      <UCard
        :ui="{
          body: '!p-0',
          header: 'border-b-0 px-6 py-5',
        }"
        class="mb-8"
      >
        <GradientTopBorder />

        <div class="flex flex-col gap-2 px-4 py-4 sm:px-6 sm:py-6">
          <DetailRow
            v-if="
              suggestion.username || suggestion.userEmail || suggestion.tokenSub
            "
            label="Submitted by"
          >
            {{
              suggestion.username ||
              suggestion.userEmail ||
              suggestion.tokenSub ||
              "Unknown"
            }}
          </DetailRow>
          <DetailRow v-if="suggestion.createdAt" label="Created">
            {{ formatDateLong(suggestion.createdAt) }}
          </DetailRow>
          <DetailRow v-if="suggestion.source" label="Source">
            {{ suggestion.source }}
          </DetailRow>
          <DetailRow label="ID">
            {{ suggestion.id }}
          </DetailRow>

          <template v-if="isCaseAnalyzer && analyzerFields.length > 0">
            <DetailRow
              v-for="field in analyzerFields"
              :key="field.label"
              :label="field.label"
            >
              <ResultValue size="sm" as="p" class="whitespace-pre-wrap">{{
                field.value
              }}</ResultValue>
            </DetailRow>
          </template>
          <template v-else>
            <DetailRow
              v-for="(value, key) in filteredPayload"
              :key="key"
              :label="formatFieldName(key)"
            >
              <ResultValue
                v-if="isLongText(value)"
                size="sm"
                as="p"
                class="whitespace-pre-wrap"
                >{{ formatValue(value) }}</ResultValue
              >
              <ResultValue v-else size="sm" as="p">{{
                formatValue(value)
              }}</ResultValue>
            </DetailRow>
          </template>
        </div>
      </UCard>

      <div class="action-bar">
        <template v-if="isActionable">
          <UButton
            v-if="!isEditSuggestion"
            color="success"
            size="lg"
            :loading="approving"
            :disabled="rejecting || deleting"
            @click="showApproveConfirm = true"
          >
            <template #leading>
              <UIcon name="i-heroicons-check-16-solid" class="h-4 w-4" />
            </template>
            Approve
          </UButton>
          <UAlert
            v-else
            color="info"
            variant="subtle"
            icon="i-heroicons-information-circle"
            title="Approval not available"
            description="Approval for edit suggestions is not yet supported. You can still reject this suggestion."
            class="flex-1"
          />
          <UButton
            color="error"
            size="lg"
            variant="subtle"
            :loading="rejecting"
            :disabled="approving || deleting"
            @click="handleReject"
          >
            <template #leading>
              <UIcon name="i-heroicons-x-mark-16-solid" class="h-4 w-4" />
            </template>
            Reject
          </UButton>
        </template>

        <UAlert
          v-else-if="suggestion?.moderationStatus"
          variant="subtle"
          icon="i-heroicons-eye"
          title="Read-only View"
          :description="`This submission has been ${getStatusLabel(suggestion.moderationStatus).toLowerCase()}.`"
          class="flex-1"
        />

        <div v-if="isCaseAnalyzer" class="ml-auto">
          <UButton
            color="error"
            size="lg"
            variant="ghost"
            :loading="deleting"
            :disabled="approving || rejecting"
            @click="showDeleteConfirm = true"
          >
            <template #leading>
              <UIcon name="i-heroicons-trash" class="h-4 w-4" />
            </template>
            Delete
          </UButton>
        </div>
      </div>
    </div>

    <UModal v-model:open="showSuccessModal">
      <template #content>
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Success</h3>
          </template>
          <p class="text-cold-slate">{{ successMessage }}</p>
          <template #footer>
            <div class="flex justify-end">
              <UButton @click="goToList"> Back to List </UButton>
            </div>
          </template>
        </UCard>
      </template>
    </UModal>

    <UModal v-model:open="showErrorModal">
      <template #content>
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold text-red-600">Error</h3>
          </template>
          <p class="text-cold-slate">{{ errorMessage }}</p>
          <template #footer>
            <div class="flex justify-end">
              <UButton @click="showErrorModal = false"> Close </UButton>
            </div>
          </template>
        </UCard>
      </template>
    </UModal>

    <UModal v-model:open="showApproveConfirm">
      <template #content>
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Confirm Approval</h3>
          </template>
          <p class="text-cold-slate">
            Are you sure you want to approve this submission? It will be
            published to the database.
          </p>
          <template #footer>
            <div class="flex justify-end gap-2">
              <UButton
                variant="ghost"
                color="neutral"
                @click="showApproveConfirm = false"
              >
                Cancel
              </UButton>
              <UButton
                color="success"
                :loading="approving"
                @click="handleApprove"
              >
                Approve
              </UButton>
            </div>
          </template>
        </UCard>
      </template>
    </UModal>

    <UModal v-model:open="showDeleteConfirm">
      <template #content>
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold text-red-600">Confirm Delete</h3>
          </template>
          <p class="text-cold-slate">
            Are you sure you want to permanently delete this analysis? This
            action cannot be undone.
          </p>
          <template #footer>
            <div class="flex justify-end gap-2">
              <UButton
                variant="ghost"
                color="neutral"
                @click="showDeleteConfirm = false"
              >
                Cancel
              </UButton>
              <UButton color="error" :loading="deleting" @click="handleDelete">
                Delete
              </UButton>
            </div>
          </template>
        </UCard>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { getCategoryLabel } from "@/config/moderationConfig";
import { useModerationApi } from "@/composables/useModerationApi";
import { getStatusBadgeColor, getStatusLabel } from "@/utils/moderationStatus";
import { formatDateLong } from "@/utils/format";
import DetailRow from "@/components/ui/DetailRow.vue";
import { ANALYZER_FIELD_MAP } from "@/types/analyzer";
import { extractStringFromPayload } from "@/utils/analyzerPayloadParser";
import { getEntityConfig } from "@/config/entityRegistry";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import GradientTopBorder from "@/components/ui/GradientTopBorder.vue";
import ResultValue from "@/components/ui/ResultValue.vue";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const toast = useToast();
const category = computed(() => route.params.category as string);
const suggestionId = computed(() => Number(route.params.id));
const categoryLabel = computed(() => getCategoryLabel(category.value));

const {
  getSuggestionDetail,
  approveSuggestion,
  rejectSuggestion,
  deleteSuggestion,
} = useModerationApi();

const { openDrawer } = useEntityDrawer();

const openOriginalEntity = () => {
  const editId = suggestion.value?.payload?.edit_entity_id;
  if (!editId) return;
  const basePath = `/${getCategoryEntityRoute(category.value)}`;
  const config = getEntityConfig(basePath);
  if (!config) return;
  openDrawer(String(editId), config.table, basePath, true);
};

const {
  data: suggestion,
  pending,
  error,
} = await useAsyncData(
  `suggestion-${category.value}-${suggestionId.value}`,
  () => getSuggestionDetail(category.value, suggestionId.value),
  { server: false },
);

const approving = ref(false);
const rejecting = ref(false);
const deleting = ref(false);
const showSuccessModal = ref(false);
const showErrorModal = ref(false);
const showApproveConfirm = ref(false);
const showDeleteConfirm = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const isCaseAnalyzer = computed(() => category.value === "case-analyzer");

const isActionable = computed(() => {
  const status = suggestion.value?.moderationStatus;
  if (!status || status === "pending") return true;
  if (isCaseAnalyzer.value && status === "completed") return true;
  return false;
});

const isEditSuggestion = computed(
  () => !!suggestion.value?.payload?.edit_entity_id,
);

const getCategoryEntityRoute = (cat: string): string => {
  const mapping: Record<string, string> = {
    "court-decisions": "court-decision",
    "domestic-instruments": "domestic-instrument",
    "regional-instruments": "regional-instrument",
    "international-instruments": "international-instrument",
    literature: "literature",
  };
  return mapping[cat] ?? cat;
};

const filteredPayload = computed(() => {
  if (!suggestion.value?.payload) return {};

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
    "raw_data",
    "draft_id",
    "notes",
    "edit_entity_id",
  ]);

  const filtered: Record<string, unknown> = {};
  const payload = suggestion.value.payload;

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
    if (metaFields.has(key) || value === null || value === "") {
      continue;
    }

    if (category.value === "case-analyzer") {
      if (
        key.endsWith("_printed") ||
        key.endsWith("_reasoning") ||
        key.endsWith("_confidence")
      ) {
        continue;
      }

      if (editedFields.has(key)) {
        continue;
      }
    }

    filtered[key] = value;
  }

  return filtered;
});

const analyzerFields = computed(() => {
  if (!suggestion.value?.payload) return [];
  const payload = suggestion.value.payload as Record<string, unknown>;
  const results: { label: string; value: string }[] = [];

  for (const [, config] of Object.entries(ANALYZER_FIELD_MAP)) {
    const extracted = extractStringFromPayload(
      payload,
      config.keys,
      config.nestedKeys ?? [],
      config.joinWith,
    );
    if (extracted) {
      results.push({ label: config.label, value: extracted });
    }
  }

  return results;
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

const handleApprove = async () => {
  showApproveConfirm.value = false;
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

const handleDelete = async () => {
  deleting.value = true;
  showDeleteConfirm.value = false;
  try {
    const result = await deleteSuggestion(category.value, suggestionId.value);
    toast.add({
      title: "Deleted",
      description: result.message || "Analysis deleted successfully!",
      color: "success",
      icon: "i-heroicons-check-circle",
      duration: 3000,
    });
    navigateTo(`/moderation/${category.value}`);
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : "Failed to delete analysis";
    showErrorModal.value = true;
    deleting.value = false;
  }
};

const goToList = () => {
  navigateTo(`/moderation/${category.value}`);
};
</script>

<style scoped>
h1,
h2,
h3 {
  font-family: "DM Sans", sans-serif;
}

.edit-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  border: 1px solid #fde68a;
  border-radius: 8px;
  background: #fffbeb;
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
