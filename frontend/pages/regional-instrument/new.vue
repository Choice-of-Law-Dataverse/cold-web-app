<template>
  <BaseDetailLayout
    :loading="false"
    :result-data="{}"
    :key-label-pairs="[]"
    :value-class-map="{}"
    source-table="Regional Instrument"
    :hide-back-button="true"
    header-mode="new"
    :show-notification-banner="true"
    :notification-banner-message="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
    @open-save-modal="openSaveModal"
    @open-cancel-modal="showCancelModal = true"
  >
    <!-- Always render this section, even if keyLabelPairs is empty -->
    <div class="section-gap m-0 p-0">
      <UFormGroup size="lg" hint="Required" :error="errors.abbreviation">
        <template #label>
          <span class="label">Abbreviation</span>
        </template>
        <UInput v-model="abbreviation" class="cold-input mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Title</span>
        </template>
        <UInput v-model="title" class="cold-input mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">URL</span>
        </template>
        <UInput v-model="url" placeholder="https://…" class="cold-input mt-2" />
      </UFormGroup>

      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label flex flex-row items-center">Date</span>
          <InfoPopover :text="tooltipRegionalInstrumentDate" />
        </template>
        <UPopover :popper="{ placement: 'bottom-start' }">
          <UButton
            icon="i-heroicons-calendar-days-20-solid"
            :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
            class="cold-date-trigger mt-2"
          />

          <template #panel="{ close }">
            <DatePicker v-model="date" @close="close" />
          </template>
        </UPopover>
      </UFormGroup>
    </div>
  </BaseDetailLayout>

  <CancelModal v-model="showCancelModal" @confirm-cancel="confirmCancel" />
  <SaveModal
    v-model="showSaveModal"
    :email="email"
    :comments="comments"
    :token="token"
    :save-modal-errors="saveModalErrors"
    :name="title"
    :specialists="specialists"
    :date="date || null"
    :pdf-file="pdfFile"
    :link="url"
    @update:email="(val) => (email = val)"
    @update:comments="(val) => (comments = val)"
    @update:token="(val) => (token = val)"
    @update:save-modal-errors="(val) => (saveModalErrors.value = val)"
    @save="handleNewSave"
  />
</template>

<script setup>
import { ref, watch } from "vue";
import { useHead, useRouter } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import tooltipRegionalInstrumentDate from "@/content/info_boxes/regional_instrument/date.md?raw";

import { format } from "date-fns";
const date = ref(null);

const config = useRuntimeConfig();

// Form data
const abbreviation = ref("");
const title = ref("");
const url = ref("");
const specialists = ref([""]);
const pdfFile = ref(null);
const email = ref("");
const comments = ref("");

const turnstile = ref();
const token = ref("");

// Ensure Submit button reactivity when token changes
watch(token, () => {
  // This will trigger reactivity for the Submit button
});

// Validation schema
const formSchema = z.object({
  abbreviation: z
    .string()
    .min(1, { message: "Abbreviation is required" })
    .min(3, { message: "Abbreviation must be at least 3 characters long" }),
});

// Form validation state
const errors = ref({});
const saveModalErrors = ref({});

const router = useRouter();
const emit = defineEmits(["close-cancel-modal", "close-save-modal"]);
const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.";

useHead({ title: "New Regional Instrument — CoLD" });

function validateForm() {
  try {
    const formData = {
      abbreviation: abbreviation.value,
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

function onPdfChange(event) {
  // Handle different event types - UInput might pass FileList directly or as event.target.files
  let file = null;
  if (event instanceof FileList) {
    file = event[0] || null;
  } else if (event && event.target && event.target.files) {
    file = event.target.files[0] || null;
  } else if (event && event.files) {
    file = event.files[0] || null;
  }
  pdfFile.value = file;
}

function confirmCancel() {
  router.push("/");
}

function addSpecialist() {
  specialists.value.push("");
}
function removeSpecialist(idx) {
  specialists.value.splice(idx, 1);
}

function handleNewSave() {
  const payload = {
    abbreviation: abbreviation.value,
    title: title.value || undefined,
    url: url.value || undefined,
    attachment: "", // ignored for now
    instrument_date:
      date.value && date.value ? format(date.value, "yyyy-MM-dd") : undefined,
    // Submitter metadata from SaveModal
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
  };

  // Explicitly log the exact payload we send
  (async () => {
    try {
      const { useApiClient } = await import("@/composables/useApiClient");
      const { apiClient } = useApiClient();
      await apiClient("/suggestions/regional-instruments", { body: payload });

      showSaveModal.value = false;
      router.push({
        path: "/confirmation",
        query: { message: "Thanks, we have received your submission." },
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

async function onSubmit() {
  const res = await $fetch("/api/submit", {
    method: "POST",
    body: { token /* form fields */ },
  });

  if (res.success) {
    // handle success
  } else {
    // handle error
  }
  turnstile.value?.reset();
}
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none !important;
}
</style>
