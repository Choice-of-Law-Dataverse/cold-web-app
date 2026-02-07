<template>
  <div>
    <BaseDetailLayout
      table="Literature"
      :loading="isLoadingEntity"
      :data="{}"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-material-symbols:warning-outline'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <h3 class="mb-4 text-lg font-semibold">
        Suggest edits to this Literature entry
      </h3>
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <!-- Title (required) -->
        <UFormField size="lg" hint="Required" :error="errors.title">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="title" class="cold-input mt-2" />
        </UFormField>

        <!-- Year (required) -->
        <UFormField size="lg" hint="Required" :error="errors.publication_year">
          <template #label>
            <span class="label">Year</span>
          </template>
          <UInput v-model="publicationYear" class="cold-input mt-2" />
        </UFormField>

        <!-- Author(s) (required) -->
        <UFormField size="lg" hint="Required" :error="errors.author">
          <template #label>
            <span class="label">Author</span>
          </template>
          <UInput v-model="author" class="cold-input mt-2" />
        </UFormField>

        <!-- Publication (optional) -->
        <UFormField size="lg" :error="errors.publication_title">
          <template #label>
            <span class="label">Publication title</span>
          </template>
          <UInput v-model="publicationTitle" class="cold-input mt-2" />
        </UFormField>

        <!-- Jurisdiction (read-only in edit mode) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">Jurisdiction</span>
          </template>
          <p
            class="result-value-small mt-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-gray-500"
          >
            {{ jurisdictionDisplay || "—" }}
          </p>
        </UFormField>

        <!-- URL (optional) -->
        <UFormField size="lg" :error="errors.url">
          <template #label>
            <span class="label">URL</span>
          </template>
          <UInput v-model="url" class="cold-input mt-2" />
        </UFormField>

        <!-- DOI (optional) -->
        <UFormField size="lg" :error="errors.doi">
          <template #label>
            <span class="label">DOI</span>
          </template>
          <UInput v-model="doi" class="cold-input mt-2" />
        </UFormField>

        <!-- Date (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">Publication date</span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="
                publicationDate
                  ? format(publicationDate, 'dd MMMM yyyy')
                  : 'Add date'
              "
              class="cold-date-trigger mt-2"
            />
            <template #content="{ close }">
              <DatePicker v-model="publicationDate" @close="close" />
            </template>
          </UPopover>
        </UFormField>

        <!-- ISBN (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">ISBN</span>
          </template>
          <UInput v-model="isbn" class="cold-input mt-2" />
        </UFormField>

        <!-- ISSN (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">ISSN</span>
          </template>
          <UInput v-model="issn" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Theme</span>
          </template>
          <UInput v-model="theme" class="cold-input mt-2" />
        </UFormField>

        <div class="flex justify-end md:col-span-2">
          <UButton
            class="bg-cold-purple hover:bg-cold-purple/90 text-white"
            @click="openSaveModal"
          >
            Submit your edits
          </UButton>
        </div>
      </div>
    </BaseDetailLayout>

    <ClientOnly>
      <CancelModal v-model="showCancelModal" @confirm-cancel="confirmCancel" />
      <SaveModal
        v-model="showSaveModal"
        :comments="comments"
        :save-modal-errors="saveModalErrors"
        :name="title"
        @update:comments="(val) => (comments = val)"
        @update:save-modal-errors="(val) => (saveModalErrors.value = val)"
        @save="handleEditSave"
      />
    </ClientOnly>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useHead, useRouter, useRoute } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format, parseISO } from "date-fns";
import { useLiterature } from "@/composables/useRecordDetails";

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const router = useRouter();
const entityId = ref(route.query.id);

const { data: entityData, isLoading: isLoadingEntity } =
  useLiterature(entityId);

const author = ref("");
const title = ref("");
const publicationTitle = ref("");
const publicationYear = ref("");
const url = ref("");
const doi = ref("");
const publicationDate = ref(null);
const isbn = ref("");
const issn = ref("");
const theme = ref("");

const jurisdictionDisplay = ref("");

const comments = ref("");

function safeParseDateString(dateStr) {
  if (!dateStr) return null;
  try {
    const parsed = parseISO(dateStr);
    return isNaN(parsed.getTime()) ? null : parsed;
  } catch {
    return null;
  }
}

// Pre-populate form when entity data loads
watch(
  entityData,
  (data) => {
    if (!data) return;
    author.value = data["Author"] || "";
    title.value = data["Title"] || "";
    publicationTitle.value = data["Publication Title"] || "";
    publicationYear.value = data["Publication Year"] || "";
    url.value = data["Url"] || data["Open Access URL"] || "";
    doi.value = data["DOI"] || "";
    isbn.value = data["ISBN"] || "";
    issn.value = data["ISSN"] || "";
    theme.value = data["Themes"] || "";

    const pubDate = safeParseDateString(data["Date"]);
    if (pubDate) publicationDate.value = pubDate;

    // Display jurisdiction (read-only)
    jurisdictionDisplay.value = data["Jurisdiction"] || "";
  },
  { immediate: true },
);

const formSchema = z.object({
  author: z
    .string()
    .min(1, { message: "Author is required" })
    .min(3, { message: "Author must be at least 3 characters long" }),
  title: z
    .string()
    .min(1, { message: "Title is required" })
    .min(3, { message: "Title must be at least 3 characters long" }),
  publication_year: z
    .string()
    .regex(/^\d{4}$/u, { message: "Year must be 4 digits (e.g., 2024)" }),
});

const errors = ref({});
const saveModalErrors = ref({});

const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "You are editing an existing Literature entry. Your changes will be submitted as a suggestion for review.";

useHead({ title: "Edit Literature — CoLD" });

function validateForm() {
  try {
    const formData = {
      author: author.value,
      title: title.value,
      publication_year: publicationYear.value,
    };
    formSchema.parse(formData);
    errors.value = {};
    return true;
  } catch (error) {
    if (error instanceof z.ZodError) {
      errors.value = {};
      error.errors.forEach((err) => {
        errors.value[err.path[0]] = err.message;
      });
    }
    return false;
  }
}

function openSaveModal() {
  const isValid = validateForm();
  if (isValid) {
    showSaveModal.value = true;
  }
}

function confirmCancel() {
  router.push(`/literature/${entityId.value}`);
}

function handleEditSave() {
  const payload = {
    edit_entity_id: entityId.value,
    author: author.value,
    title: title.value,
    publication_title: publicationTitle.value || undefined,
    publication_year: Number(publicationYear.value),
    url: url.value || undefined,
    doi: doi.value || undefined,
    publication_date:
      publicationDate.value && publicationDate.value
        ? format(publicationDate.value, "yyyy-MM-dd")
        : undefined,
    isbn: isbn.value || undefined,
    issn: issn.value || undefined,
    theme: theme.value || undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      await $fetch(`/api/proxy/suggestions/literature`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          source: "cold.global",
        },
        body: payload,
      });
      showSaveModal.value = false;
      router.push({
        path: "/confirmation",
        query: {
          message: "Thanks, we have received your edit suggestion for review.",
        },
      });
    } catch (err) {
      saveModalErrors.value = {
        general:
          "There was a problem submitting your suggestion. Please try again.",
      };
      console.error("Submission failed:", err);
    }
  })();
}
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none !important;
}
</style>
