<template>
  <div>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="isLoadingEntity"
      :data="{}"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-heroicons-pencil-square'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <h3 class="mb-4 text-lg font-semibold">
        Suggest edits to this Domestic Instrument
      </h3>
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
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

        <UFormField size="lg" :error="errors.official_title" hint="Required">
          <template #label>
            <span class="label flex flex-row items-center">
              Official Title
              <InfoPopover :text="tooltipOfficialTitle" />
            </span>
          </template>
          <UInput
            v-model="officialTitle"
            class="cold-input mt-2"
            placeholder="e.g. Bundesgesetz über das Internationale Privatrecht"
          />
        </UFormField>

        <UFormField size="lg" :error="errors.title_en" hint="Required">
          <template #label>
            <span class="label flex flex-row items-center">
              Name
              <InfoPopover :text="tooltipDomesticInstrumentTitle" />
            </span>
          </template>
          <UInput
            v-model="titleEn"
            class="cold-input mt-2"
            placeholder="e.g. Swiss Private International Law Act"
          />
        </UFormField>

        <UFormField size="lg" hint="Required" :error="errors.entry_into_force">
          <template #label>
            <span class="label flex flex-row items-center">
              Entry Into Force
              <InfoPopover :text="tooltipEntryIntoForce" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="format(entryIntoForce, 'dd MMMM yyyy')"
              class="cold-date-trigger mt-2"
            />
            <template #content="{ close }">
              <DatePicker v-model="entryIntoForce" is-required @close="close" />
            </template>
          </UPopover>
        </UFormField>

        <UFormField size="lg" hint="Required" :error="errors.source_url">
          <template #label>
            <span class="label">Source (URL)</span>
          </template>
          <UInput
            v-model="sourceUrl"
            class="cold-input mt-2"
            placeholder="https://…"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Themes</span>
          </template>
          <UInput v-model="themes" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Status</span>
          </template>
          <UInput v-model="status" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Publication Date
              <InfoPopover :text="tooltipDomesticInstrumentPublicationDate" />
            </span>
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

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Abbreviation
              <InfoPopover :text="tooltipAbbreviation" />
            </span>
          </template>
          <UInput v-model="abbreviation" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Compatible With the HCCH Principles?
              <InfoPopover :text="tooltipCompatibleWithHCCH" />
            </span>
          </template>
          <div
            class="cold-toggle-group mt-2"
            role="group"
            aria-label="Compatible with the HCCH Principles"
          >
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="compatibleHcchPrinciples === 'No'"
              @click="compatibleHcchPrinciples = 'No'"
            >
              No
            </UButton>
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="compatibleHcchPrinciples === 'Yes'"
              @click="compatibleHcchPrinciples = 'Yes'"
            >
              Yes
            </UButton>
          </div>
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Compatible With the UNCITRAL Model Law?
              <InfoPopover :text="tooltipCompatibleWithUNCITRAL" />
            </span>
          </template>
          <div
            class="cold-toggle-group mt-2"
            role="group"
            aria-label="Compatible with the UNCITRAL Model Law"
          >
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="compatibleUncitralModelLaw === 'No'"
              @click="compatibleUncitralModelLaw = 'No'"
            >
              No
            </UButton>
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="compatibleUncitralModelLaw === 'Yes'"
              @click="compatibleUncitralModelLaw = 'Yes'"
            >
              Yes
            </UButton>
          </div>
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
        :name="titleEn"
        :date="entryIntoForce"
        :link="sourceUrl"
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
import DatePicker from "@/components/ui/DatePicker.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format, parseISO } from "date-fns";
import { domesticInstrumentTooltips } from "@/config/tooltips";
import { useDomesticInstrument } from "@/composables/useRecordDetails";

const tooltipAbbreviation = domesticInstrumentTooltips["Abbreviation"];
const tooltipCompatibleWithHCCH = domesticInstrumentTooltips["Compatibility"];
const tooltipCompatibleWithUNCITRAL =
  domesticInstrumentTooltips["Compatibility"];
const tooltipEntryIntoForce = domesticInstrumentTooltips["Entry Into Force"];
const tooltipOfficialTitle = domesticInstrumentTooltips["Official Title"];
const tooltipDomesticInstrumentPublicationDate =
  domesticInstrumentTooltips["Publication Date"];
const tooltipDomesticInstrumentTitle =
  domesticInstrumentTooltips["Title (in English)"];

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const router = useRouter();
const entityId = ref(route.query.id);

const { data: entityData, isLoading: isLoadingEntity } =
  useDomesticInstrument(entityId);

const officialTitle = ref("");
const titleEn = ref("");
const jurisdictionDisplay = ref("");
const entryIntoForce = ref(new Date());
const sourceUrl = ref("");
const themes = ref("");
const status = ref("");
const publicationDate = ref(null);
const abbreviation = ref("");
const compatibleHcchPrinciples = ref(undefined);
const compatibleUncitralModelLaw = ref(undefined);

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
    officialTitle.value = data["Official Title"] || "";
    titleEn.value = data["Title (in English)"] || "";
    sourceUrl.value = data["Source (URL)"] || "";
    themes.value = data["Themes"] || "";
    status.value = data["Status"] || "";
    abbreviation.value = data["Abbreviation"] || "";

    const entryDate = safeParseDateString(data["Entry Into Force"]);
    if (entryDate) entryIntoForce.value = entryDate;

    const pubDate = safeParseDateString(data["Publication Date"]);
    if (pubDate) publicationDate.value = pubDate;

    if (data["Compatible With the HCCH Principles"] === true) {
      compatibleHcchPrinciples.value = "Yes";
    } else if (data["Compatible With the HCCH Principles"] === false) {
      compatibleHcchPrinciples.value = "No";
    }

    if (data["Compatible With the UNCITRAL Model Law"] === true) {
      compatibleUncitralModelLaw.value = "Yes";
    } else if (data["Compatible With the UNCITRAL Model Law"] === false) {
      compatibleUncitralModelLaw.value = "No";
    }

    // Display jurisdiction (read-only)
    jurisdictionDisplay.value =
      data["Jurisdictions"] || data["Jurisdiction"] || "";
  },
  { immediate: true },
);

const formSchema = z.object({
  official_title: z
    .string()
    .min(1, { message: "Official title is required" })
    .min(3, { message: "Official title must be at least 3 characters long" }),
  title_en: z
    .string()
    .min(1, { message: "English title is required" })
    .min(3, { message: "English title must be at least 3 characters long" }),
  entry_into_force: z.date({ required_error: "Entry into force is required" }),
  source_url: z.string().url({
    message: 'Source link must be a valid URL starting with "https://"',
  }),
});

const errors = ref({});
const saveModalErrors = ref({});

const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "You are editing an existing Domestic Instrument. Your changes will be submitted as a suggestion for review.";

useHead({ title: "Edit Domestic Instrument — CoLD" });

function validateForm() {
  try {
    const formData = {
      official_title: officialTitle.value,
      title_en: titleEn.value,
      entry_into_force: entryIntoForce.value,
      source_url: sourceUrl.value,
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
  router.push(`/domestic-instrument/${entityId.value}`);
}

function handleEditSave() {
  const payload = {
    edit_entity_id: entityId.value,
    jurisdiction_link: jurisdictionDisplay.value || undefined,
    official_title: officialTitle.value,
    title_en: titleEn.value,
    entry_into_force: format(entryIntoForce.value, "yyyy-MM-dd"),
    source_url: sourceUrl.value,
    themes: themes.value
      ? themes.value
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t)
      : undefined,
    status: status.value || undefined,
    publication_date: publicationDate.value
      ? format(publicationDate.value, "yyyy-MM-dd")
      : undefined,
    abbreviation: abbreviation.value || undefined,
    compatible_hcch_principles:
      compatibleHcchPrinciples.value !== undefined
        ? compatibleHcchPrinciples.value
        : undefined,
    compatible_uncitral_model_law:
      compatibleUncitralModelLaw.value !== undefined
        ? compatibleUncitralModelLaw.value
        : undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      await $fetch(`/api/proxy/suggestions/domestic-instruments`, {
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
