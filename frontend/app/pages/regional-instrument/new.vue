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
      <div class="m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
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
            <ColdDateTrigger
              icon="i-heroicons-calendar-days-20-solid"
              :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
              class="mt-2"
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

const tooltipRegionalInstrumentDate = tooltips.date ?? "";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "New Regional Instrument — CoLD" });

const date = ref<Date | undefined>(undefined);
const abbreviation = ref("");
const title = ref("");
const url = ref("");
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
  endpoint: "/suggestions/regional-instruments",
  schema: z.object({
    abbreviation: z
      .string()
      .min(1, { error: "Abbreviation is required" })
      .min(3, { error: "Abbreviation must be at least 3 characters long" }),
  }),
  values: () => ({ abbreviation: abbreviation.value }),
  payload: () => ({
    abbreviation: abbreviation.value,
    title: title.value || undefined,
    url: url.value || undefined,
    instrument_date: date.value ? format(date.value, "yyyy-MM-dd") : undefined,
  }),
});
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none;
}
</style>
