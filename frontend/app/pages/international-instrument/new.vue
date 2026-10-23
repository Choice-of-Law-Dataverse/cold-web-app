<template>
  <div>
    <BaseDetailLayout
      table="International Instruments"
      :loading="false"
      :data="null"
      header-mode="new"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.name">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="name" class="mt-2" />
        </UFormField>
        <UFormField size="lg" hint="Required" :error="errors.link">
          <template #label>
            <span class="label flex flex-row items-center">
              Link
              <InfoPopover :text="tooltipInternationalInstrumentLink" />
            </span>
          </template>
          <UInput v-model="link" class="mt-2" placeholder="https://…" />
        </UFormField>
        <UFormField size="lg" hint="Required" :error="errors.instrument_date">
          <template #label>
            <span class="label flex flex-row items-center">
              Date
              <InfoPopover :text="tooltipInternationalInstrumentDate" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <ColdDateTrigger
              icon="i-heroicons-calendar-days-20-solid"
              :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
              class="mt-2"
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
      <CancelModal v-model="showCancelModal" @confirm-cancel="cancel" />
      <SaveModal
        v-model:open="isSaveModalOpen"
        v-model:comments="comments"
        :submitting="isSubmitting"
        :error="submitError"
        @submit="submit"
      />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useHead } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format } from "date-fns";
import { tooltips } from "@/config/tooltips";
import ColdDateTrigger from "@/components/ui/ColdDateTrigger.vue";
import { useSuggestionForm } from "@/composables/useSuggestionForm";

const tooltipInternationalInstrumentDate = tooltips.date ?? "";
const tooltipInternationalInstrumentLink =
  "Link to the official source or full text of the instrument.";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "New International Instrument — CoLD" });

const date = ref(new Date());
const name = ref("");
const link = ref("");
const showCancelModal = ref(false);

const {
  errors,
  comments,
  isSaveModalOpen,
  isSubmitting,
  submitError,
  openSaveModal,
  submit,
  cancel,
} = useSuggestionForm({
  endpoint: "/suggestions/international-instruments",
  schema: z.object({
    name: z
      .string()
      .min(1, { error: "Title is required" })
      .min(3, { error: "Title must be at least 3 characters long" }),
    link: z.url({ error: 'URL must be valid and start with "https://"' }),
    instrument_date: z.date({ error: "Date is required" }),
  }),
  values: () => ({
    name: name.value,
    link: link.value,
    instrument_date: date.value,
  }),
  payload: () => ({
    name: name.value,
    url: link.value,
    instrument_date: date.value ? format(date.value, "yyyy-MM-dd") : "",
  }),
});
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none;
}
</style>
