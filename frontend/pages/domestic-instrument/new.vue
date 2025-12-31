<template>
  <div>
    <BaseDetailLayout
      :loading="false"
      :result-data="{}"
      :key-label-pairs="[]"
      :value-class-map="{}"
      source-table="Domestic Instrument"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-material-symbols:warning-outline'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 p-0">
        <UFormGroup size="lg" hint="Required" :error="errors.jurisdiction_link">
          <template #label>
            <span class="label">Jurisdiction</span>
          </template>
          <SearchFilters
            v-model="selectedJurisdiction"
            :options="jurisdictionOptions"
            class="mt-2 w-full"
            show-avatars="true"
            :multiple="false"
          />
        </UFormGroup>

        <UFormGroup
          size="lg"
          class="mt-8"
          :error="errors.official_title"
          hint="Required"
        >
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
        </UFormGroup>

        <UFormGroup
          size="lg"
          class="mt-8"
          :error="errors.title_en"
          hint="Required"
        >
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
        </UFormGroup>

        <UFormGroup
          size="lg"
          class="mt-8"
          hint="Required"
          :error="errors.entry_into_force"
        >
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
            <template #panel="{ close }">
              <DatePicker v-model="entryIntoForce" is-required @close="close" />
            </template>
          </UPopover>
        </UFormGroup>

        <UFormGroup
          size="lg"
          class="mt-8"
          hint="Required"
          :error="errors.source_url"
        >
          <template #label>
            <span class="label">Source (URL)</span>
          </template>
          <UInput
            v-model="sourceUrl"
            class="cold-input mt-2"
            placeholder="https://…"
          />
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
          <template #label>
            <span class="label">Themes</span>
          </template>
          <UInput v-model="themes" class="cold-input mt-2" />
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
          <template #label>
            <span class="label">Status</span>
          </template>
          <UInput v-model="status" class="cold-input mt-2" />
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
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
            <template #panel="{ close }">
              <DatePicker v-model="publicationDate" @close="close" />
            </template>
          </UPopover>
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
          <template #label>
            <span class="label flex flex-row items-center">
              Abbreviation
              <InfoPopover :text="tooltipAbbreviation" />
            </span>
          </template>
          <UInput v-model="abbreviation" class="cold-input mt-2" />
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
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
        </UFormGroup>

        <UFormGroup size="lg" class="mt-8">
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
      :name="titleEn"
      :specialists="specialists"
      :date="entryIntoForce"
      :pdf-file="pdfFile"
      :link="sourceUrl"
      @update:email="(val) => (email = val)"
      @update:comments="(val) => (comments = val)"
      @update:token="(val) => (token = val)"
      @update:save-modal-errors="(val) => (saveModalErrors.value = val)"
      @save="handleNewSave"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useHead, useRouter } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import SearchFilters from "@/components/search-results/SearchFilters.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import { format } from "date-fns";
import tooltipAbbreviation from "@/content/info_boxes/domestic_instrument/abbreviation.md?raw";
import tooltipCompatibleWithHCCH from "@/content/info_boxes/domestic_instrument/compatible_hcch.md?raw";
import tooltipCompatibleWithUNCITRAL from "@/content/info_boxes/domestic_instrument/compatible_uncitral.md?raw";
import tooltipEntryIntoForce from "@/content/info_boxes/domestic_instrument/entry_into_force.md?raw";
import tooltipOfficialTitle from "@/content/info_boxes/domestic_instrument/official_title.md?raw";
import tooltipDomesticInstrumentPublicationDate from "@/content/info_boxes/domestic_instrument/publication_date.md?raw";
import tooltipDomesticInstrumentTitle from "@/content/info_boxes/domestic_instrument/title.md?raw";

definePageMeta({
  middleware: ["auth"],
});

const officialTitle = ref("");
const titleEn = ref("");
const selectedJurisdiction = ref([]);
const jurisdictionOptions = ref([{ label: "All Jurisdictions" }]);
const entryIntoForce = ref(new Date());
const sourceUrl = ref("");
const themes = ref("");
const status = ref("");
const publicationDate = ref(null);
const abbreviation = ref("");
const compatibleHcchPrinciples = ref(undefined);
const compatibleUncitralModelLaw = ref(undefined);

const specialists = ref([""]);
const pdfFile = ref(null);
const email = ref("");
const comments = ref("");

const token = ref("");

watch(token, () => {});

const loadJurisdictions = async () => {
  try {
    const response = await fetch(`/api/proxy/search/full_table`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ table: "Jurisdictions", filters: [] }),
    });

    if (!response.ok) throw new Error("Failed to load jurisdictions");

    const jurisdictionsData = await response.json();
    jurisdictionOptions.value = [
      { label: "Select Jurisdiction" },
      ...jurisdictionsData
        .filter((entry) => entry["Irrelevant?"] === false)
        .map((entry) => ({
          label: entry.Name,
          avatar: entry["Alpha-3 Code"]
            ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${entry["Alpha-3 Code"].toLowerCase()}.svg`
            : undefined,
        }))
        .sort((a, b) => (a.label || "").localeCompare(b.label || "")),
    ];
  } catch (error) {
    console.error("Error loading jurisdictions:", error);
  }
};

onMounted(loadJurisdictions);

const formSchema = z.object({
  jurisdiction_link: z
    .string()
    .min(1, { message: "Selected jurisdiction is required" }),
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

const router = useRouter();
const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.";

useHead({ title: "New Domestic Instrument — CoLD" });

function validateForm() {
  try {
    const formData = {
      jurisdiction_link:
        (Array.isArray(selectedJurisdiction.value) &&
          selectedJurisdiction.value[0]?.label) ||
        "",
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
  router.push("/");
}

function handleNewSave() {
  const payload = {
    jurisdiction_link:
      (Array.isArray(selectedJurisdiction.value) &&
        selectedJurisdiction.value[0]?.label) ||
      undefined,
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
    submitter_email: email.value || undefined,
    submitter_comments: comments.value || undefined,
    source: "cold.global",
  };

  (async () => {
    try {
      await $fetch(`/api/proxy/suggestions/domestic-instruments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: payload,
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
