<template>
  <BaseDetailLayout
    table="Arbitral Awards"
    page-heading="Arbitral Awards"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="awards-filters mb-6 flex flex-wrap gap-4">
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
        <div class="awards-table">
          <UTable :columns="columns" :data="rows">
            <template #caseNumber-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.caseNumber }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.caseNumber }}</span
              >
            </template>
            <template #year-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.original.year }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.year
              }}</span>
            </template>
            <template #seatTown-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.seatTown
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.seatTown
              }}</span>
            </template>
            <template #source-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.source
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.source
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/arbitral-award/${row.original.coldId}`"
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
import type { JurisdictionOption } from "@/types/analyzer";
import themeOptions from "@/assets/themeOptions.json";

useHead({
  title: "Arbitral Awards — CoLD",
});

const page = ref(1);
const pageSize = 200;
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const selectedTheme = ref<string | undefined>(undefined);

const { data: jurisdictions } = useJurisdictions();

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

const hasActiveFilter = computed(
  () => Boolean(jurisdictionCode.value) || Boolean(selectedTheme.value),
);

watch([jurisdictionCode, selectedTheme], () => {
  page.value = 1;
});

function onJurisdictionChange(j: JurisdictionOption | undefined) {
  selectedJurisdiction.value = j;
}

function resetFilters() {
  selectedJurisdiction.value = undefined;
  selectedTheme.value = undefined;
}

const { data, isLoading } = useEntityList("arbitral-awards", {
  page,
  pageSize,
  jurisdiction: jurisdictionCode,
  theme: selectedTheme,
});

const sanitize = (v: unknown) =>
  v == null || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    caseNumber: sanitize(item.caseNumber),
    year: sanitize(item.year),
    seatTown: sanitize(item.seatTown),
    source: sanitize(item.source),
    coldId: sanitize(item.coldId),
  })),
);

const columns = [
  { id: "caseNumber", accessorKey: "caseNumber", header: "Case Number" },
  { id: "year", accessorKey: "year", header: "Year" },
  { id: "seatTown", accessorKey: "seatTown", header: "Seat (Town)" },
  { id: "source", accessorKey: "source", header: "Source" },
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

.awards-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.awards-table :deep(th),
.awards-table :deep(td) {
  box-sizing: border-box;
  width: 125px;
  min-width: 125px;
  max-width: 125px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.awards-table :deep(th:nth-child(4)),
.awards-table :deep(td:nth-child(4)) {
  width: 225px;
  min-width: 225px;
  max-width: 225px;
}

.awards-table :deep(th:last-child),
.awards-table :deep(td:last-child) {
  padding-right: 16px;
  text-align: right;
}

.awards-table :deep(td:last-child a.label) {
  font-weight: 600;
  font-size: 12px;
}

.awards-table :deep(tbody tr) {
  height: 72px;
}
.awards-table :deep(tbody td) {
  height: 72px;
  vertical-align: top;
}

.awards-table :deep(tbody td:first-child) {
  padding-top: 10px;
}

.awards-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.awards-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.awards-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.awards-table :deep(thead th span),
.awards-table :deep(thead th button),
.awards-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.awards-table :deep(thead th button:hover),
.awards-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.awards-table :deep(thead th button:hover span),
.awards-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
