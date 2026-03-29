<template>
  <div class="py-12">
    <div class="mb-8 flex items-center gap-3">
      <NuxtLink
        to="/moderation"
        class="border-cold-gray text-cold-slate hover:border-cold-purple hover:text-cold-purple flex h-8 w-8 items-center justify-center rounded-lg border transition-colors"
      >
        <UIcon name="i-heroicons-arrow-left-16-solid" class="h-4 w-4" />
      </NuxtLink>
      <div>
        <h1 class="text-cold-night text-2xl font-bold tracking-tight">
          {{ categoryLabel }}
        </h1>
        <p class="text-cold-slate text-sm">
          <template v-if="isCaseAnalyzer">All submissions</template>
          <template v-else>Pending review</template>
          <template v-if="suggestions">
            &middot; {{ suggestions.length }}
            {{ suggestions.length === 1 ? "item" : "items" }}
          </template>
        </p>
      </div>
    </div>

    <div v-if="pending" class="flex justify-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin" />
    </div>

    <UAlert
      v-else-if="error"
      color="error"
      variant="subtle"
      title="Error"
      :description="error.message"
      class="mb-4"
    />

    <div
      v-else-if="!suggestions || suggestions.length === 0"
      class="empty-state"
    >
      <UIcon
        name="i-heroicons-check-circle"
        class="text-cold-green mx-auto h-12 w-12"
      />
      <p class="text-cold-night mt-3 font-medium">
        {{ isCaseAnalyzer ? "No submissions yet" : "Queue is clear" }}
      </p>
      <p class="text-cold-slate mt-1 text-sm">
        {{
          isCaseAnalyzer
            ? "New submissions will appear here."
            : "No items pending review."
        }}
      </p>
    </div>

    <div v-else class="suggestion-list">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="suggestion-row"
        :class="{
          'suggestion-row--disabled': !isClickable(suggestion),
          'suggestion-row--clickable': isClickable(suggestion),
        }"
        @click="isClickable(suggestion) && handleCardClick(suggestion)"
      >
        <div class="flex min-w-0 flex-1 items-start gap-4">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <h3 class="text-cold-night truncate text-sm font-semibold">
                {{ getSuggestionTitle(suggestion) }}
              </h3>
              <UBadge
                v-if="suggestion.payload?.edit_entity_id"
                color="warning"
                variant="subtle"
                size="xs"
              >
                Edit
              </UBadge>
            </div>

            <p
              v-if="getSuggestionSubtitle(suggestion)"
              class="text-cold-slate mt-0.5 truncate text-xs"
            >
              {{ getSuggestionSubtitle(suggestion) }}
            </p>

            <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span
                v-if="
                  getPreciseJurisdiction(suggestion) ||
                  getJurisdiction(suggestion)
                "
                class="meta-item"
              >
                <JurisdictionFlag
                  :iso3="
                    getJurisdictionISO(
                      getPreciseJurisdiction(suggestion) ||
                        getJurisdiction(suggestion),
                    )
                  "
                  size="xs"
                />
                {{
                  getPreciseJurisdiction(suggestion) ||
                  getJurisdiction(suggestion)
                }}
              </span>
              <span v-if="getSuggestionDate(suggestion)" class="meta-item">
                <UIcon
                  name="i-heroicons-calendar-16-solid"
                  class="h-3.5 w-3.5"
                />
                {{ getSuggestionDate(suggestion) }}
              </span>
              <span
                v-if="suggestion.username || suggestion.userEmail"
                class="meta-item"
              >
                <UIcon name="i-heroicons-user-16-solid" class="h-3.5 w-3.5" />
                {{ suggestion.username || suggestion.userEmail }}
              </span>
              <span v-if="suggestion.source" class="meta-item">
                <UIcon
                  name="i-heroicons-arrow-top-right-on-square-16-solid"
                  class="h-3.5 w-3.5"
                />
                {{ suggestion.source }}
              </span>
              <span v-if="suggestion.createdAt" class="meta-item">
                <UIcon name="i-heroicons-clock-16-solid" class="h-3.5 w-3.5" />
                {{ formatDateLong(suggestion.createdAt) }}
              </span>
            </div>
          </div>

          <UBadge
            :color="getStatusBadgeColor(suggestion.moderationStatus)"
            variant="subtle"
            size="xs"
          >
            {{ getStatusLabel(suggestion.moderationStatus) }}
          </UBadge>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getCategoryLabel } from "@/config/moderationConfig";
import { useModerationApi } from "@/composables/useModerationApi";
import type { PendingSuggestion } from "@/composables/useModerationApi";
import { getStatusBadgeColor, getStatusLabel } from "@/utils/moderationStatus";
import { formatDateLong } from "@/utils/format";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";

definePageMeta({
  middleware: ["moderation"],
});

const route = useRoute();
const category = computed(() => route.params.category as string);
const categoryLabel = computed(() => getCategoryLabel(category.value));
const isCaseAnalyzer = computed(() => category.value === "case-analyzer");

const { listPendingSuggestions } = useModerationApi();
const { getJurisdictionISO } = useJurisdictionLookup();

const {
  data: suggestions,
  pending,
  error,
} = await useAsyncData(
  `pending-${category.value}`,
  () => listPendingSuggestions(category.value, isCaseAnalyzer.value),
  {
    watch: [category],
    server: false,
  },
);

const extractValue = (raw: unknown): string => {
  if (!raw) return "";
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) return raw[0] ? String(raw[0]) : "";
  if (typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    for (const key of Object.keys(obj)) {
      if (
        key !== "reasoning" &&
        key !== "confidence" &&
        typeof obj[key] === "string"
      ) {
        return obj[key] as string;
      }
    }
  }
  return String(raw);
};

const getSuggestionTitle = (suggestion: PendingSuggestion): string => {
  if ("caseCitation" in suggestion && suggestion.caseCitation) {
    return String(suggestion.caseCitation);
  }

  const payload = suggestion.payload || {};
  const titleFields = [
    "case_citation",
    "case_name",
    "title",
    "title_en",
    "official_title",
    "name",
    "abbreviation",
    "citation",
    "publication_title",
  ];
  for (const field of titleFields) {
    if (payload[field]) {
      const value = extractValue(payload[field]);
      if (value) return value;
    }
  }
  if (payload.author) return extractValue(payload.author);
  return `Entry #${suggestion.id}`;
};

const getSuggestionSubtitle = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const parts: string[] = [];
  const author = extractValue(payload.author);
  if (author) parts.push(author);
  const abbr = extractValue(payload.abbreviation);
  const title = extractValue(payload.title);
  if (abbr && title) parts.push(abbr);
  const official = extractValue(payload.official_title);
  const titleEn = extractValue(payload.title_en);
  if (official && titleEn) parts.push(official);
  return parts.join(" · ");
};

const getSuggestionDate = (suggestion: PendingSuggestion): string => {
  const payload = suggestion.payload || {};
  const dateFields = [
    "date_of_judgment",
    "decision_date",
    "date",
    "instrument_date",
    "date_publication",
    "entry_into_force",
    "publication_date",
    "year",
    "publication_year",
  ];
  for (const field of dateFields) {
    const val = extractValue(payload[field]);
    if (val) return val;
  }
  return "";
};

const getJurisdiction = (suggestion: PendingSuggestion): string => {
  const p = suggestion.payload || {};
  const raw = p.jurisdiction || p.country;
  if (!raw) return "";
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) return raw[0] ? String(raw[0]) : "";
  if (typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    if (typeof obj.precise_jurisdiction === "string")
      return obj.precise_jurisdiction;
    if (typeof obj.jurisdiction_code === "string") return obj.jurisdiction_code;
  }
  return "";
};

const getPreciseJurisdiction = (suggestion: PendingSuggestion): string => {
  const p = suggestion.payload || {};
  if (typeof p.precise_jurisdiction === "string") return p.precise_jurisdiction;
  if (typeof p.precise_jurisdiction_edited === "string")
    return p.precise_jurisdiction_edited;
  const jur = p.jurisdiction;
  if (jur && typeof jur === "object" && !Array.isArray(jur)) {
    const obj = jur as Record<string, unknown>;
    if (typeof obj.precise_jurisdiction === "string")
      return obj.precise_jurisdiction;
  }
  return "";
};

const isClickable = (suggestion: PendingSuggestion): boolean => {
  if (isCaseAnalyzer.value) {
    const status = suggestion.moderationStatus;
    return status !== "approved" && status !== "rejected";
  }
  return true;
};

const handleCardClick = (suggestion: PendingSuggestion) => {
  if (isClickable(suggestion)) {
    navigateTo(`/moderation/${category.value}/${suggestion.id}`);
  }
};
</script>

<style scoped>
h1,
h2,
h3 {
  font-family: "DM Sans", sans-serif;
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  border: 1px dashed var(--color-cold-gray);
  border-radius: 12px;
  background: var(--gradient-subtle);
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-cold-gray);
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.suggestion-row {
  display: flex;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-cold-gray);
  transition:
    background 0.15s ease,
    opacity 0.15s ease;
}

.suggestion-row:last-child {
  border-bottom: none;
}

.suggestion-row--clickable {
  cursor: pointer;
}

.suggestion-row--clickable:hover {
  background: var(--gradient-subtle);
}

.suggestion-row--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-cold-slate);
}
</style>
