<template>
  <div>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="false"
      :data="null"
      header-mode="new"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.jurisdiction_link">
          <template #label>
            <span class="label">Jurisdiction</span>
          </template>
          <SearchFilters
            v-model="selectedJurisdiction"
            :options="jurisdictionOptions"
            class="mt-2 w-full"
            :show-avatars="true"
            :multiple="false"
          />
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
            class="mt-2"
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
            class="mt-2"
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
          <UInput v-model="sourceUrl" class="mt-2" placeholder="https://…" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Themes</span>
          </template>
          <UInput v-model="themes" class="mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Status</span>
          </template>
          <UInput v-model="status" class="mt-2" />
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
          <UInput v-model="abbreviation" class="mt-2" />
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
        :name="titleEn"
        :specialists="specialists"
        :date="entryIntoForce"
        :pdf-file="pdfFile"
        :link="sourceUrl"
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
import { ref, onMounted } from "vue";
import { useHead, useRouter } from "#imports";
import { z } from "zod";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DatePicker from "@/components/ui/DatePicker.vue";
import SearchFilters from "@/components/search-results/SearchFilters.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format } from "date-fns";
import { tooltips } from "@/config/tooltips";
import { flagUrl } from "@/config/assets";

interface JurisdictionEntry {
  name: string;
  coldId?: string;
  irrelevant?: boolean;
}

interface JurisdictionOption {
  label: string;
  coldId?: string;
  avatar?: string;
}

const tooltipAbbreviation = tooltips.abbreviation ?? "";
const tooltipCompatibleWithHCCH = tooltips.compatibility ?? "";
const tooltipCompatibleWithUNCITRAL = tooltips.compatibility ?? "";
const tooltipEntryIntoForce = tooltips.entryIntoForce ?? "";
const tooltipOfficialTitle = tooltips.officialTitle ?? "";
const tooltipDomesticInstrumentPublicationDate = tooltips.publicationDate ?? "";
const tooltipDomesticInstrumentTitle = tooltips.titleInEnglish ?? "";

definePageMeta({
  middleware: ["auth"],
});

const officialTitle = ref("");
const titleEn = ref("");
const selectedJurisdiction = ref<JurisdictionOption[]>([]);
const jurisdictionOptions = ref<JurisdictionOption[]>([
  { label: "All Jurisdictions" },
]);
const entryIntoForce = ref(new Date());
const sourceUrl = ref("");
const themes = ref("");
const status = ref("");
const publicationDate = ref<Date | undefined>(undefined);
const abbreviation = ref("");
const compatibleHcchPrinciples = ref<string | undefined>(undefined);
const compatibleUncitralModelLaw = ref<string | undefined>(undefined);

const specialists = ref([""]);
const pdfFile = ref<File | null>(null);
const email = ref("");
const comments = ref("");

const loadJurisdictions = async () => {
  try {
    const response = await fetch(
      `/api/proxy/search/full_table?table=Jurisdictions`,
    );

    if (!response.ok) throw new Error("Failed to load jurisdictions");

    const jurisdictionsData: JurisdictionEntry[] = await response.json();
    jurisdictionOptions.value = [
      { label: "Select Jurisdiction" },
      ...jurisdictionsData
        .filter((entry: JurisdictionEntry) => entry.irrelevant !== true)
        .map((entry: JurisdictionEntry) => ({
          label: entry.name,
          coldId: entry.coldId,
          avatar: entry.coldId ? flagUrl(entry.coldId) : undefined,
        }))
        .sort((a, b) => (a.label || "").localeCompare(b.label || "")),
    ];
  } catch {
    /* jurisdiction load is best-effort */
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

const errors = ref<Record<string, string>>({});
const saveModalErrors = ref<Record<string, string>>({});

const router = useRouter();
const showSaveModal = ref(false);
const showCancelModal = ref(false);

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
