<template>
  <div>
    <BaseDetailLayout
      table="Literature"
      :loading="false"
      :data="null"
      header-mode="new"
      :show-notification-banner="true"
      :notification-banner-message="notificationBannerMessage"
      :icon="'i-material-symbols:warning-outline'"
      @open-save-modal="openSaveModal"
      @open-cancel-modal="showCancelModal = true"
    >
      <div class="section-gap m-0 grid grid-cols-1 gap-8 p-0 md:grid-cols-2">
        <!-- Title (required) -->
        <UFormField size="lg" hint="Required" :error="errors.title">
          <template #label>
            <span class="label">Title</span>
          </template>
          <UInput v-model="title" class="mt-2" />
        </UFormField>

        <!-- Year (required) -->
        <UFormField size="lg" hint="Required" :error="errors.publication_year">
          <template #label>
            <span class="label">Year</span>
          </template>
          <UInput v-model="publicationYear" class="mt-2" />
        </UFormField>

        <!-- Author(s) (required) -->
        <UFormField size="lg" hint="Required" :error="errors.author">
          <template #label>
            <span class="label">Author</span>
          </template>
          <UInput v-model="author" class="mt-2" />
        </UFormField>

        <!-- Publication (optional) -->
        <UFormField size="lg" :error="errors.publication_title">
          <template #label>
            <span class="label">Publication title</span>
          </template>
          <UInput v-model="publicationTitle" class="mt-2" />
        </UFormField>

        <!-- Jurisdiction (optional) -->
        <UFormField size="lg">
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

        <!-- URL (optional) -->
        <UFormField size="lg" :error="errors.url">
          <template #label>
            <span class="label">URL</span>
          </template>
          <UInput v-model="url" class="mt-2" />
        </UFormField>

        <!-- DOI (optional) -->
        <UFormField size="lg" :error="errors.doi">
          <template #label>
            <span class="label">DOI</span>
          </template>
          <UInput v-model="doi" class="mt-2" />
        </UFormField>

        <!-- Date (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">Publication date</span>
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

        <!-- ISBN (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">ISBN</span>
          </template>
          <UInput v-model="isbn" class="mt-2" />
        </UFormField>

        <!-- ISSN (optional) -->
        <UFormField size="lg">
          <template #label>
            <span class="label">ISSN</span>
          </template>
          <UInput v-model="issn" class="mt-2" />
        </UFormField>

        <UFormField size="lg">
          <template #label>
            <span class="label">Theme</span>
          </template>
          <UInput v-model="theme" class="mt-2" />
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
import SaveModal from "@/components/ui/SaveModal.vue";
import CancelModal from "@/components/ui/CancelModal.vue";
import { format } from "date-fns";
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

definePageMeta({
  middleware: ["auth"],
});

const author = ref("");
const title = ref("");
const publicationTitle = ref("");
const publicationYear = ref("");
const url = ref("");
const doi = ref("");
const publicationDate = ref<Date | undefined>(undefined);
const isbn = ref("");
const issn = ref("");
const theme = ref("");

const selectedJurisdiction = ref<JurisdictionOption[]>([]);
const jurisdictionOptions = ref<JurisdictionOption[]>([
  { label: "All Jurisdictions" },
]);

const email = ref("");
const comments = ref("");

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
  author: z
    .string()
    .min(1, { message: "Author is required" })
    .min(3, { message: "Author must be at least 3 characters long" }),
  title: z
    .string()
    .min(1, { message: "Title is required" })
    .min(3, { message: "Title must be at least 3 characters long" }),
  publication_year: z
    .string()
    .regex(/^\d{4}$/u, { message: "Year must be 4 digits (e.g., 2024)" }),
});

const errors = ref<Record<string, string>>({});
const saveModalErrors = ref<Record<string, string>>({});

const router = useRouter();
const showSaveModal = ref(false);
const showCancelModal = ref(false);
const notificationBannerMessage =
  "Please back up your data when working here. Leaving, closing or reloading this window will delete everything. Data is only saved after you submit.";

useHead({ title: "New Literature — CoLD" });

function validateForm() {
  try {
    const formData = {
      author: author.value,
      title: title.value,
      publication_year: publicationYear.value,
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
    author: author.value,
    title: title.value,
    publication_title: publicationTitle.value || undefined,
    publication_year: Number(publicationYear.value),
    url: url.value || undefined,
    doi: doi.value || undefined,
    publication_date:
      publicationDate.value && publicationDate.value
        ? format(publicationDate.value, "yyyy-MM-dd")
        : undefined,
    isbn: isbn.value || undefined,
    issn: issn.value || undefined,
    jurisdiction:
      (Array.isArray(selectedJurisdiction.value) &&
        selectedJurisdiction.value[0]?.label) ||
      undefined,
    theme: theme.value || undefined,
    submitter_comments: comments.value || undefined,
  };

  (async () => {
    try {
      await $fetch(`/api/proxy/suggestions/literature`, {
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
