<template>
  <div>
    <BaseDetailLayout
      table="Court Decisions"
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
        Suggest edits to this Court Decision
      </h3>
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <UFormField size="lg" hint="Required" :error="errors.case_citation">
          <template #label>
            <span class="label flex flex-row items-center">
              Case citation
              <InfoPopover :text="tooltipCaseCitation" />
            </span>
          </template>
          <UInput v-model="caseCitation" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg" hint="Required">
          <template #label>
            <span class="label flex flex-row items-center">
              Publication Date
              <InfoPopover :text="tooltipPublicationDate" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="format(datePublication, 'dd MMMM yyyy')"
              class="cold-date-trigger mt-2"
            />
            <template #content="{ close }">
              <DatePicker
                v-model="datePublication"
                is-required
                @close="close"
              />
            </template>
          </UPopover>
        </UFormField>

        <UFormField
          size="lg"
          hint="Required"
          :error="errors.official_source_url"
        >
          <template #label>
            <span class="label">Official source (URL)</span>
          </template>
          <UInput
            v-model="officialSourceUrl"
            placeholder="https://…"
            class="cold-input mt-2"
          />
        </UFormField>

        <UFormField size="lg" hint="Required" :error="errors.copyright_issues">
          <template #label>
            <span class="label">Copyright issues</span>
          </template>
          <div
            class="cold-toggle-group mt-2"
            role="group"
            aria-label="Copyright issues"
          >
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="copyrightIssues === 'No'"
              @click="copyrightIssues = 'No'"
            >
              No
            </UButton>
            <UButton
              class="cold-toggle-btn"
              :aria-pressed="copyrightIssues === 'Yes'"
              @click="copyrightIssues = 'Yes'"
            >
              Yes
            </UButton>
          </div>
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Full Text</span>
          </template>
          <UTextarea
            v-model="caseFullText"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">English Translation of Full Text</span>
          </template>
          <UTextarea
            v-model="caseEnglishTranslation"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Case Rank</span>
          </template>
          <UInput v-model="caseRank" class="cold-input mt-2" />
        </UFormField>

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

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Abstract
              <InfoPopover :text="tooltipAbstract" />
            </span>
          </template>
          <UTextarea
            v-model="caseAbstract"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Relevant Facts
              <InfoPopover :text="tooltipRelevantFacts" />
            </span>
          </template>
          <UTextarea
            v-model="caseRelevantFacts"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              PIL Provisions
              <InfoPopover :text="tooltipPILProvisions" />
            </span>
          </template>
          <UInput v-model="casePILProvisions" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Choice of Law Issue
              <InfoPopover :text="tooltipChoiceofLawIssue" />
            </span>
          </template>
          <UTextarea
            v-model="caseChoiceofLawIssue"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Court's Position
              <InfoPopover :text="tooltipCourtsPosition" />
            </span>
          </template>
          <UTextarea
            v-model="caseCourtsPosition"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center"
              >Translated Excerpt</span
            >
          </template>
          <UTextarea
            v-model="caseTranslatedExcerpt"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center"
              >Text of the Relevant Legal Provisions</span
            >
          </template>
          <UTextarea
            v-model="caseTextofRelevantLegalProvisions"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Quote
              <InfoPopover :text="tooltipQuote" />
            </span>
          </template>
          <UTextarea
            v-model="caseQuote"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Judgment Date
              <InfoPopover :text="tooltipJudgmentDate" />
            </span>
          </template>
          <UPopover :popper="{ placement: 'bottom-start' }">
            <UButton
              icon="i-heroicons-calendar-days-20-solid"
              :label="
                dateJudgment ? format(dateJudgment, 'dd MMMM yyyy') : 'Add date'
              "
              class="cold-date-trigger mt-2"
            />
            <template #content="{ close }">
              <DatePicker v-model="dateJudgment" @close="close" />
            </template>
          </UPopover>
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Case Title
              <InfoPopover :text="tooltipCaseTitle" />
            </span>
          </template>
          <UInput v-model="caseTitle" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center">
              Instance
              <InfoPopover :text="tooltipInstance" />
            </span>
          </template>
          <UInput v-model="caseInstance" class="cold-input mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label flex flex-row items-center"
              >Official Keywords</span
            >
          </template>
          <UTextarea
            v-model="caseOfficialKeywords"
            class="cold-input mt-2 min-h-[140px] resize-y"
            :rows="6"
          />
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
        :name="caseCitation"
        :date="datePublication"
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
import { courtDecisionTooltips } from "@/config/tooltips";
import { useCourtDecision } from "@/composables/useRecordDetails";

const tooltipAbstract = courtDecisionTooltips["Abstract"];
const tooltipCaseCitation = courtDecisionTooltips["Case Citation"];
const tooltipCaseTitle = courtDecisionTooltips["Case Title"];
const tooltipChoiceofLawIssue = courtDecisionTooltips["Choice of Law Issue"];
const tooltipCourtsPosition = courtDecisionTooltips["Court's Position"];
const tooltipInstance = courtDecisionTooltips["Instance"];
const tooltipJudgmentDate = courtDecisionTooltips["Date of Judgment"];
const tooltipPILProvisions = courtDecisionTooltips["PIL Provisions"];
const tooltipPublicationDate = courtDecisionTooltips["Publication Date ISO"];
const tooltipQuote = courtDecisionTooltips["Quote"];
const tooltipRelevantFacts = courtDecisionTooltips["Relevant Facts"];

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const router = useRouter();
const entityId = ref(route.query.id);

// Fetch existing entity data
const { data: entityData, isLoading: isLoadingEntity } =
  useCourtDecision(entityId);

const caseCitation = ref("");
const caseTitle = ref("");
const caseFullText = ref("");
const caseEnglishTranslation = ref("");
const caseRank = ref("");
const caseAbstract = ref("");
const caseRelevantFacts = ref("");
const casePILProvisions = ref("");
const caseChoiceofLawIssue = ref("");
const caseCourtsPosition = ref("");
const caseTranslatedExcerpt = ref("");
const caseTextofRelevantLegalProvisions = ref("");
const caseQuote = ref("");
const caseInstance = ref("");
const caseOfficialKeywords = ref("");
const officialSourceUrl = ref("");
const copyrightIssues = ref("No");
const datePublication = ref(new Date());
const dateJudgment = ref(null);

const email = ref("");
const comments = ref("");

const jurisdictionDisplay = ref("");

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
    caseCitation.value = data["Case Citation"] || "";
    caseTitle.value =
      data["Case Title"] === "Not found" ? "" : data["Case Title"] || "";
    caseFullText.value = data["Original Text"] || "";
    caseEnglishTranslation.value = data["English Translation"] || "";
    caseRank.value = data["Case Rank"] || "";
    caseAbstract.value = data["Abstract"] || "";
    caseRelevantFacts.value = data["Relevant Facts"] || "";
    casePILProvisions.value = data["PIL Provisions"] || "";
    caseChoiceofLawIssue.value = data["Choice of Law Issue"] || "";
    caseCourtsPosition.value = data["Court's Position"] || "";
    caseTranslatedExcerpt.value = data["Translated Excerpt"] || "";
    caseTextofRelevantLegalProvisions.value =
      data["Text of the Relevant Legal Provisions"] ||
      data["Text_of_the_Relevant_Legal_Provisions"] ||
      "";
    caseQuote.value = data["Quote"] || "";
    caseInstance.value = data["Instance"] || "";
    caseOfficialKeywords.value = data["Official Keywords"] || "";
    officialSourceUrl.value = data["Official Source (URL)"] || "";

    const pubDate = safeParseDateString(data["Publication Date ISO"]);
    if (pubDate) datePublication.value = pubDate;

    const judgDate = safeParseDateString(data["Date of Judgment"]);
    if (judgDate) dateJudgment.value = judgDate;

    // Display jurisdiction (read-only)
    jurisdictionDisplay.value =
      data["Jurisdictions"] || data["Jurisdiction"] || "";
  },
  { immediate: true },
);

const formSchema = z.object({
  case_citation: z
    .string()
    .min(1, { message: "Case citation is required" })
    .min(3, { message: "Case citation must be at least 3 characters long" }),
  official_source_url: z.string().url({
    message: 'Link must be a valid URL. It must start with "https://"',
  }),
});

const errors = ref({});
const saveModalErrors = ref({});

const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "You are editing an existing Court Decision. Your changes will be submitted as a suggestion for review.";

useHead({ title: "Edit Court Decision — CoLD" });

function validateForm() {
  try {
    const formData = {
      case_citation: caseCitation.value,
      date_publication: datePublication.value,
      official_source_url: officialSourceUrl.value,
      copyright_issues: copyrightIssues.value,
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
  router.push(`/court-decision/${entityId.value}`);
}

function handleEditSave() {
  const payload = {
    edit_entity_id: entityId.value,
    case_citation: caseCitation.value,
    date_publication: format(datePublication.value, "yyyy-MM-dd"),
    official_source_url: officialSourceUrl.value,
    copyright_issues: copyrightIssues.value,
    original_text: caseFullText.value,
    english_translation: caseEnglishTranslation.value,
    case_rank: caseRank.value,
    abstract: caseAbstract.value,
    relevant_facts: caseRelevantFacts.value,
    pil_provisions: casePILProvisions.value,
    choice_of_law_issue: caseChoiceofLawIssue.value,
    courts_position: caseCourtsPosition.value,
    translated_excerpt: caseTranslatedExcerpt.value,
    text_of_relevant_legal_provisions: caseTextofRelevantLegalProvisions.value,
    quote: caseQuote.value,
    decision_date: dateJudgment.value
      ? format(dateJudgment.value, "yyyy-MM-dd")
      : undefined,
    case_title: caseTitle.value,
    instance: caseInstance.value,
    official_keywords: caseOfficialKeywords.value,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      await $fetch(`/api/proxy/suggestions/court-decisions`, {
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
:deep(.card-header__actions) {
  display: none !important;
}
:deep(.card-header [class*="actions"]) {
  display: none !important;
}
</style>
