<template>
  <div v-if="isEditPage">
    <BaseDetailLayout
      table="International Instruments"
      :loading="loading"
      :data="{}"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-material-symbols:warning-outline'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 p-0">
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
        <UFormField size="lg" class="mt-8">
          <template #label>
            <span class="label">Specialists</span>
            <InfoPopover :text="tooltipInternationalInstrumentSpecialist" />
          </template>
          <div
            v-for="(specialist, idx) in specialists"
            :key="idx"
            class="mt-2 flex items-center"
          >
            <UInput
              v-model="specialists[idx]"
              placeholder="Specialist’s name"
              class="flex-1"
            />
            <UButton
              v-if="idx > 0"
              icon="i-heroicons-x-mark"
              color="error"
              variant="ghost"
              class="ml-2"
              aria-label="Remove specialist"
              @click="removeSpecialist(idx)"
            />
          </div>
          <template v-for="(specialist, idx) in specialists">
            <div
              v-if="specialists[idx] && idx === specialists.length - 1"
              :key="'add-btn-' + idx"
            >
              <UButton
                class="mt-2"
                color="primary"
                variant="soft"
                icon="i-heroicons-plus"
                @click="addSpecialist"
                >Add another specialist</UButton
              >
            </div>
          </template>
        </UFormField>
        <UFormField size="lg" class="mt-8">
          <template #label>
            <span class="label">PDF</span>
            <InfoPopover :text="tooltipInternationalInstrumentSpecialist" />
          </template>
          <UInput
            type="file"
            icon="i-material-symbols:upload-file"
            @change="onPdfChange"
          />
          <div v-if="pdfFileName" class="mt-2 text-sm text-gray-500">
            Current: {{ pdfFileName }}
          </div>
        </UFormField>
        <UFormField size="lg" class="mt-8" :error="errors.link">
          <template #label>
            <span class="label">Link</span>
            <InfoPopover :text="tooltipInternationalInstrumentLink" />
          </template>
          <UInput v-model="link" class="mt-2" placeholder="Link" />
        </UFormField>
        <UFormField size="lg" class="mt-8">
          <template #label>
            <span class="label">Date</span>
            <InfoPopover :text="tooltipInternationalInstrumentDate" />
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="format(date, 'dd MMMM yyyy')"
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
      <CancelModal v-model="showCancelModal" @confirm-cancel="confirmCancel" />
      <SaveModal
        v-model="showSaveModal"
        :email="email"
        :comments="comments"
        :save-modal-errors="saveModalErrors"
        :name="name"
        :specialists="specialists"
        :date="date"
        :pdf-file="pdfFile"
        :link="link"
        :instrument-id="instrumentApiId"
        @update:email="(val) => (email = val)"
        @update:comments="(val) => (comments = val)"
        @update:save-modal-errors="(val) => (saveModalErrors.value = val)"
        @save="handleEditSave"
      />
    </ClientOnly>
  </div>
  <div v-else>Page not found</div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { z } from "zod";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format, parseISO } from "date-fns";
import { useHead } from "#imports";
import { internationalInstrumentTooltips } from "@/config/tooltips";

const tooltipInternationalInstrumentSpecialist =
  internationalInstrumentTooltips["Specialists"];
const tooltipInternationalInstrumentDate =
  internationalInstrumentTooltips["Date"];
const tooltipInternationalInstrumentLink =
  "Link to the official source or full text of the instrument.";

const route = useRoute();
const router = useRouter();
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
const specialists = ref([""]);
const pdfFile = ref(null);
const pdfFileName = ref("");
const date = ref(new Date());
const email = ref("");
const comments = ref("");
const errors = ref({});
const saveModalErrors = ref({});
const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.";
const instrumentApiId = ref(null);

const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: "Name is required" })
    .min(3, { message: "Name must be at least 3 characters long" }),
  specialists: z.array(z.string()).optional(),
  link: z
    .string()
    .url({ message: 'Link must be a valid URL. It must start with "https://"' })
    .optional()
    .or(z.literal("")),
});

function validateForm() {
  try {
    const formData = {
      name: name.value,
      specialists: specialists.value,
      link: link.value,
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
  let file = null;
  if (event instanceof FileList) {
    file = event[0] || null;
  } else if (event && event.target && event.target.files) {
    file = event.target.files[0] || null;
  } else if (event && event.files) {
    file = event.files[0] || null;
  }
  pdfFile.value = file;
  pdfFileName.value = file ? file.name : "";
}

function addSpecialist() {
  specialists.value.push("");
}
function removeSpecialist(idx) {
  specialists.value.splice(idx, 1);
}

function confirmCancel() {
  if (isEditPage.value && instrumentId.value) {
    router.push(`/international-instrument/${instrumentId.value}`);
  } else {
    router.push("/");
  }
}

function handleEditSave() {
  showSaveModal.value = false;
  navigateTo(
    {
      path: "/confirmation",
      query: {
        message: "Thanks, we have received your edit suggestions.",
      },
    },
    { replace: true },
  );
}

async function fetchInstrument() {
  loading.value = true;
  try {
    if (!instrumentId.value) {
      loading.value = false;
      return;
    }

    const response = await fetch(`/api/proxy/search/details`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        table: "International Instruments",
        id: instrumentId.value,
      }),
    });
    const responseText = await response.text();
    if (!response.ok) throw new Error("Failed to fetch instrument");
    const data = JSON.parse(responseText);
    name.value = data["Name"] || data["Title (in English)"] || "";
    specialists.value = data["Specialists"]
      ? data["Specialists"].split(",").map((s) => s.trim())
      : [""];
    date.value = data["Date"] ? parseISO(data["Date"]) : new Date();
    link.value = data["URL"] || "";
    pdfFileName.value = data["PDF"] || "";
    instrumentApiId.value = data["ID"] || null;
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
        link: [
          {
            rel: "canonical",
            href: `https://cold.global${route.fullPath}`,
          },
        ],
        meta: [
          {
            name: "description",
            content: pageTitle,
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
  display: none !important;
}
</style>
