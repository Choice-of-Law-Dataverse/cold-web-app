<template>
  <div>
    <BaseDetailLayout
      table="Regional Instruments"
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
        Suggest edits to this Regional Instrument
      </h3>
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.abbreviation">
          <template #label>
            <span class="label">Abbreviation</span>
          </template>
          <UInput v-model="abbreviation" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="title" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">URL</span>
          </template>
          <UInput
            v-model="url"
            placeholder="https://…"
            class="cold-input mt-2"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Date
              <InfoPopover :text="tooltipRegionalInstrumentDate" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
              class="cold-date-trigger mt-2"
            />

            <template #content="{ close }">
              <DatePicker v-model="date" @close="close" />
            </template>
          </UPopover>
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
        :email="email"
        :comments="comments"
        :save-modal-errors="saveModalErrors"
        :name="title"
        :date="date || null"
        :link="url"
        @update:email="(val) => (email = val)"
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
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format, parseISO } from "date-fns";
import { regionalInstrumentTooltips } from "@/config/tooltips";
import { useRegionalInstrument } from "@/composables/useRecordDetails";

const tooltipRegionalInstrumentDate = regionalInstrumentTooltips["Date"];

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const router = useRouter();
const entityId = ref(route.query.id);

const { data: entityData, isLoading: isLoadingEntity } =
  useRegionalInstrument(entityId);

const date = ref(null);
const abbreviation = ref("");
const title = ref("");
const url = ref("");
const email = ref("");
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
    abbreviation.value = data["Abbreviation"] || "";
    title.value = data["Title"] || data["Title (in English)"] || "";
    url.value = data["URL"] || data["Link"] || "";

    const instrumentDate = safeParseDateString(data["Date"]);
    if (instrumentDate) date.value = instrumentDate;
  },
  { immediate: true },
);

const formSchema = z.object({
  abbreviation: z
    .string()
    .min(1, { message: "Abbreviation is required" })
    .min(3, { message: "Abbreviation must be at least 3 characters long" }),
});

const errors = ref({});
const saveModalErrors = ref({});

const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "You are editing an existing Regional Instrument. Your changes will be submitted as a suggestion for review.";

useHead({ title: "Edit Regional Instrument — CoLD" });

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

function confirmCancel() {
  router.push(`/regional-instrument/${entityId.value}`);
}

function handleEditSave() {
  const payload = {
    edit_entity_id: entityId.value,
    abbreviation: abbreviation.value,
    title: title.value || undefined,
    url: url.value || undefined,
    instrument_date: date.value ? format(date.value, "yyyy-MM-dd") : undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      const { useApiClient } = await import("@/composables/useApiClient");
      const { apiClient } = useApiClient();
      await apiClient("/suggestions/regional-instruments", {
        body: payload,
        headers: {
          source: "cold.global",
        },
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
