<template>
  <BaseDetailLayout
    table="Court Decisions"
    page-heading="Court Decisions"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="court-decision-filters mb-6 flex flex-wrap gap-4">
          <div class="filter-control">
            <label class="filter-label">Jurisdiction</label>
            <JurisdictionSelectMenu
              v-if="jurisdictions"
              :jurisdictions="jurisdictions"
              :model-value="selectedJurisdiction"
              placeholder="All jurisdictions"
              @update:model-value="onJurisdictionChange"
            />
          </div>
          <div class="filter-control">
            <label class="filter-label">Theme</label>
            <USelectMenu
              v-model="selectedTheme"
              :items="themeOptions"
              placeholder="Any"
              size="xl"
              class="w-56"
            />
          </div>
          <div class="filter-control">
            <label class="filter-label">Case rank</label>
            <USelectMenu
              v-model="selectedCaseRank"
              :items="caseRankOptions"
              placeholder="Any"
              size="xl"
              class="w-40"
            />
          </div>
          <div v-if="hasActiveFilter" class="filter-control filter-reset">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-material-symbols:close"
              @click="resetFilters"
            >
              Clear filters
            </UButton>
          </div>
        </div>

        <div class="court-decision-table">
          <UTable :columns="columns" :data="rows">
            <template #caseTitle-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/court-decision/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.caseTitle }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.caseTitle }}</span
              >
            </template>
            <template #caseCitation-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/court-decision/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.caseCitation
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.caseCitation
              }}</span>
            </template>
            <template #date-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/court-decision/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.original.date }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.date
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/court-decision/${row.original.coldId}`"
                class="table-row-link arrow-cell"
              >
                <UIcon
                  name="i-material-symbols:arrow-forward"
                  class="arrow-icon"
                />
              </NuxtLink>
              <span v-else class="text-gray-400">—</span>
            </template>
          </UTable>
        </div>

        <EntityListPagination
          v-if="data && data.total > pageSize"
          v-model:page="page"
          :total="data.total"
          :page-size="pageSize"
        />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityListPagination from "@/components/layout/EntityListPagination.vue";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import { useEntityList } from "@/composables/useEntityList";
import { useJurisdictions } from "@/composables/useJurisdictions";
import { formatDate } from "@/utils/format";
import type { JurisdictionOption } from "@/types/analyzer";
import themeOptions from "@/assets/themeOptions.json";

useHead({
  title: "Court Decisions — CoLD",
});

const page = ref(1);
const pageSize = 250;
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const selectedTheme = ref<string | undefined>(undefined);
const caseRankOptions = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];
const selectedCaseRank = ref<string | undefined>(undefined);

const { data: jurisdictions } = useJurisdictions();

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

const hasActiveFilter = computed(
  () =>
    Boolean(jurisdictionCode.value) ||
    Boolean(selectedTheme.value) ||
    Boolean(selectedCaseRank.value),
);

watch([jurisdictionCode, selectedTheme, selectedCaseRank], () => {
  page.value = 1;
});

function onJurisdictionChange(j: JurisdictionOption | undefined) {
  selectedJurisdiction.value = j;
}

function resetFilters() {
  selectedJurisdiction.value = undefined;
  selectedTheme.value = undefined;
  selectedCaseRank.value = undefined;
}

const { data, isLoading } = useEntityList("court-decisions", {
  page,
  pageSize,
  jurisdiction: jurisdictionCode,
  theme: selectedTheme,
  caseRank: selectedCaseRank,
});

const sanitize = (v: unknown) =>
  v == null || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    caseTitle: sanitize(item.caseTitle),
    caseCitation: sanitize(item.caseCitation),
    date: formatDate(sanitize(item.publicationDateIso)) || "",
    coldId: sanitize(item.coldId),
  })),
);

const columns = [
  { id: "caseTitle", accessorKey: "caseTitle", header: "Case Title" },
  { id: "caseCitation", accessorKey: "caseCitation", header: "Citation" },
  { id: "date", accessorKey: "date", header: "Date" },
  { id: "open", accessorKey: "coldId", header: "" },
];
</script>

<style scoped>
.filter-label {
  display: block;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
  margin-bottom: 4px;
}

.filter-control {
  min-width: 200px;
}

.filter-reset {
  display: flex;
  align-items: flex-end;
  min-width: auto;
}

.court-decision-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.court-decision-table :deep(th),
.court-decision-table :deep(td) {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.court-decision-table :deep(th:first-child),
.court-decision-table :deep(td:first-child) {
  width: 50%;
}

.court-decision-table :deep(th:nth-child(2)),
.court-decision-table :deep(td:nth-child(2)) {
  width: auto;
}

.court-decision-table :deep(th:nth-child(3)),
.court-decision-table :deep(td:nth-child(3)) {
  width: 130px;
  min-width: 130px;
  max-width: 130px;
}

.court-decision-table :deep(th:last-child),
.court-decision-table :deep(td:last-child) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  padding-right: 16px;
  text-align: right;
}

.court-decision-table :deep(tbody tr) {
  height: 72px;
}
.court-decision-table :deep(tbody td) {
  height: 72px;
  vertical-align: middle;
}

.court-decision-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.court-decision-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.court-decision-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.court-decision-table :deep(thead th span),
.court-decision-table :deep(thead th button),
.court-decision-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.court-decision-table :deep(thead th button:hover),
.court-decision-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.court-decision-table :deep(thead th button:hover span),
.court-decision-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
