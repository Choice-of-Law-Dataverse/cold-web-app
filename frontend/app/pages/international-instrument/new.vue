<template>
  <div>
    <BaseDetailLayout
      table="International Instruments"
      :loading="false"
      :data="{}"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-material-symbols:warning-outline'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.name">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="name" class="cold-input mt-2" />
        </UFormField>
        <UFormField size="lg" hint="Required" :error="errors.link">
          <template #label>
            <span class="label flex flex-row items-center">
              Link
              <InfoPopover :text="tooltipInternationalInstrumentLink" />
            </span>
          </template>
          <UInput
            v-model="link"
            class="cold-input mt-2"
            placeholder="https://…"
          />
        </UFormField>
        <UFormField size="lg" hint="Required" :error="errors.instrument_date">
          <template #label>
            <span class="label flex flex-row items-center">
              Date
              <InfoPopover :text="tooltipInternationalInstrumentDate" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
              class="cold-date-trigger mt-2"
            />

            <template #content="{ close }">
              <DatePicker v-model="date" is-required @close="close" />
            </template>
          </UPopover>
        </UFormField>

        <div class="flex justify-end md:col-span-2">
          <UButton
            class="bg-cold-purple hover:bg-cold-purple/90 text-white"
            @click="openSaveModal"
          >
            Submit your data
          </UButton>
        </div>
      </div>
    </BaseDetailLayout>

    <ClientOnly>
      <LazyCancelModal
        v-model="showCancelModal"
        @confirm-cancel="confirmCancel"
      />
      <LazySaveModal
        v-model="showSaveModal"
        :email="email"
        :comments="comments"
        :save-modal-errors="saveModalErrors"
        :name="name"
        :specialists="specialists"
        :date="date"
        :pdf-file="pdfFile"
        :link="link"
        @update:email="(val) => (email = val)"
        @update:comments="(val) => (comments = val)"
        @update:save-modal-errors="(val) => (saveModalErrors.value = val)"
        @save="handleNewSave"
      />
    </ClientOnly>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useHead, useRouter } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import { format } from "date-fns";
import { internationalInstrumentTooltips } from "@/config/tooltips";

const tooltipInternationalInstrumentDate =
  internationalInstrumentTooltips["Date"];
const tooltipInternationalInstrumentLink =
  "Link to the official source or full text of the instrument.";

definePageMeta({
  middleware: ["auth"],
});

const date = ref(new Date());

const name = ref("");
const link = ref("");
const specialists = ref([""]);
const pdfFile = ref(null);
const email = ref("");
const comments = ref("");

const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: "Title is required" })
    .min(3, { message: "Title must be at least 3 characters long" }),
  link: z
    .string()
    .min(1, { message: "URL is required" })
    .url({ message: 'URL must be valid and start with "https://"' }),
  instrument_date: z.date({ required_error: "Date is required" }),
});

const errors = ref({});
const saveModalErrors = ref({});

const router = useRouter();
const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.";

useHead({ title: "New International Instrument — CoLD" });

function validateForm() {
  try {
    const formData = {
      name: name.value,
      link: link.value,
      instrument_date: date.value,
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
  router.push("/");
}

function handleNewSave() {
  const payload = {
    name: name.value,
    url: link.value,
    attachment: "", // ignored for now
    instrument_date:
      date.value && date.value ? format(date.value, "yyyy-MM-dd") : undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      const { useApiClient } = await import("@/composables/useApiClient");
      const { apiClient } = useApiClient();
      await apiClient("/suggestions/international-instruments", {
        body: payload,
        headers: {
          source: "cold.global",
        },
      });

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
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none !important;
}
</style>
