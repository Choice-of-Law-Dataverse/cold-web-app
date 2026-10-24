<template>
  <div v-if="isEditPage">
    <BaseDetailLayout
      table="International Instruments"
      :loading="loading"
      :data="null"
      header-mode="new"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="m-0 p-0">
        <UFormField size="lg" hint="Required" :error="errors.name">
          <template #label>
            <span class="label">Name</span>
          </template>
          <UInput
            v-model="name"
            class="mt-2"
            placeholder="Name of the International Instrument"
          />
        </UFormField>
        <UFormField size="lg" class="mt-8" :error="errors.link">
          <template #label>
            <span class="label">Link</span>
            <InfoPopover :text="tooltipInternationalInstrumentLink" />
          </template>
          <UInput v-model="link" class="mt-2" placeholder="Link" />
        </UFormField>
        <UFormField
          size="lg"
          class="mt-8"
          hint="Required"
          :error="errors.instrument_date"
        >
          <template #label>
            <span class="label">Date</span>
            <InfoPopover :text="tooltipInternationalInstrumentDate" />
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="date ? format(date, 'dd MMMM yyyy') : 'Add date'"
              class="mt-2"
            />
            <template #content="{ close }">
              <DatePicker v-model="date" is-required @close="close" />
            </template>
          </UPopover>
        </UFormField>
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
  <div v-else>Page not found</div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRoute, useHead } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format, parseISO } from "date-fns";
import { tooltips } from "@/config/tooltips";
import { useSuggestionForm } from "@/composables/useSuggestionForm";

definePageMeta({
  middleware: ["auth"],
  // The single-segment detail route owns normal instrument pages. This
  // catch-all is only for `/international-instrument/{coldId}/edit`.
  validate: (route) => {
    const slug = route.params.slug;
    return Array.isArray(slug) && slug.length === 2 && slug[1] === "edit";
  },
});

const tooltipInternationalInstrumentDate = tooltips.date ?? "";
const tooltipInternationalInstrumentLink =
  "Link to the official source or full text of the instrument.";

const route = useRoute();
const isEditPage = computed(() => {
  const slug = route.params.slug;
  return Array.isArray(slug) && slug.length === 2 && slug[1] === "edit";
});
const instrumentId = computed(() => {
  const slug = route.params.slug;
  return Array.isArray(slug) ? slug[0] : null;
});

const loading = ref(true);
const name = ref("");
const link = ref("");
const date = ref<Date | undefined>(undefined);
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
      .min(1, { error: "Name is required" })
      .min(3, { error: "Name must be at least 3 characters long" }),
    link: z
      .url({ error: 'Link must be a valid URL. It must start with "https://"' })
      .or(z.literal("")),
    instrument_date: z.date({ error: "Date is required" }),
  }),
  values: () => ({
    name: name.value,
    link: link.value,
    instrument_date: date.value,
  }),
  payload: () => ({
    edit_entity_id: instrumentId.value ?? undefined,
    name: name.value,
    url: link.value,
    instrument_date: date.value ? format(date.value, "yyyy-MM-dd") : "",
  }),
  successMessage: "Thanks, we have received your edit suggestions.",
  cancelTo: () =>
    instrumentId.value
      ? `/international-instrument/${instrumentId.value}`
      : "/",
});

async function fetchInstrument() {
  loading.value = true;
  try {
    if (!instrumentId.value) {
      loading.value = false;
      return;
    }

    const params = new URLSearchParams({
      table: "International Instruments",
      id: instrumentId.value,
    });
    const response = await fetch(`/api/proxy/search/details?${params}`);
    const responseText = await response.text();
    if (!response.ok) throw new Error("Failed to fetch instrument");
    const data = JSON.parse(responseText);
    name.value = data.name || data.titleInEnglish || "";
    date.value = data.date ? parseISO(data.date) : undefined;
    link.value = data.url || "";
  } catch {
    // noop
  } finally {
    loading.value = false;
  }
}

watch(
  [isEditPage, instrumentId],
  ([edit, id]) => {
    if (edit && id) {
      fetchInstrument();
    }
  },
  { immediate: true },
);

watch(
  [isEditPage, name],
  ([edit, currentName]) => {
    if (edit) {
      const pageTitle =
        currentName && currentName.trim()
          ? `Edit ${currentName} — CoLD`
          : "Edit International Instrument — CoLD";
      useHead({
        title: pageTitle,
        meta: [
          {
            name: "robots",
            content: "noindex, nofollow",
          },
        ],
      });
    }
  },
  { immediate: true },
);
</script>

<style scoped>
:deep(.card-header__actions),
:deep(.card-header [class*="actions"]) {
  display: none;
}
</style>
