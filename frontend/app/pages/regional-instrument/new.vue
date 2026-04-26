<template>
  <div>
    <BaseDetailLayout
      table="Regional Instruments"
      :loading="false"
      :data="null"
      header-mode="new"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.abbreviation">
          <template #label>
            <span class="label">Abbreviation</span>
          </template>
          <UInput v-model="abbreviation" class="mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="title" class="mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">URL</span>
          </template>
          <UInput v-model="url" placeholder="https://…" class="mt-2" />
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
            Submit your data
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
        :specialists="specialists"
        :date="date || null"
        :pdf-file="pdfFile"
        :link="url"
        @update:email="(val: string) => (email = val)"
        @update:comments="(val: string) => (comments = val)"
        @update:save-modal-errors="
          (val: Record<string, string>) => (saveModalErrors = val)
        "
        @save="handleNewSave"
      />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useHead, useRouter } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format } from "date-fns";
import { tooltips } from "@/config/tooltips";

const tooltipRegionalInstrumentDate = tooltips.date ?? "";

definePageMeta({
  middleware: ["auth"],
});

const date = ref<Date | undefined>(undefined);

const abbreviation = ref("");
const title = ref("");
const url = ref("");
const specialists = ref([""]);
const pdfFile = ref<File | null>(null);
const email = ref("");
const comments = ref("");

const formSchema = z.object({
  abbreviation: z
    .string()
    .min(1, { message: "Abbreviation is required" })
    .min(3, { message: "Abbreviation must be at least 3 characters long" }),
});

const errors = ref<Record<string, string>>({});
const saveModalErrors = ref<Record<string, string>>({});

const router = useRouter();
defineEmits(["close-cancel-modal", "close-save-modal"]);
const showSaveModal = ref(false);
const showCancelModal = ref(false);

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
      for (const err of error.errors) {
        const field = String(err.path[0]);
        errors.value[field] = err.message;
      }
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
    abbreviation: abbreviation.value,
    title: title.value || undefined,
    url: url.value || undefined,
    instrument_date: date.value ? format(date.value, "yyyy-MM-dd") : undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      const { useApiClient } = await import("@/composables/useApiClient");
      const { client } = useApiClient();
      const { error } = await client.POST("/suggestions/regional-instruments", {
        body: payload,
      });
      if (error) throw error;

      showSaveModal.value = false;
      router.push({
        path: "/confirmation",
        query: { message: "Thanks, we have received your submission." },
      });
    } catch {
      saveModalErrors.value = {
        general:
          "There was a problem submitting your suggestion. Please try again.",
      };
    }
  })();
}
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none;
}
</style>
