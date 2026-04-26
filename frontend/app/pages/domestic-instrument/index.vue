<template>
  <BaseDetailLayout
    table="Domestic Instruments"
    page-heading="Domestic Instruments"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="instrument-filters mb-6 flex flex-wrap gap-4">
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

        <div class="instrument-table">
          <UTable :columns="columns" :data="rows">
            <template #title-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/domestic-instrument/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.title }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.title }}</span
              >
            </template>
            <template #abbreviation-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/domestic-instrument/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.abbreviation
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.abbreviation
              }}</span>
            </template>
            <template #date-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/domestic-instrument/${row.original.coldId}`"
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
                :to="`/domestic-instrument/${row.original.coldId}`"
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

useHead({
  title: "Domestic Instruments — CoLD",
});

const page = ref(1);
const pageSize = 200;
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

const { data: jurisdictions } = useJurisdictions();

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

const hasActiveFilter = computed(() => Boolean(jurisdictionCode.value));

watch(jurisdictionCode, () => {
  page.value = 1;
});

function onJurisdictionChange(j: JurisdictionOption | undefined) {
  selectedJurisdiction.value = j;
}

function resetFilters() {
  selectedJurisdiction.value = undefined;
}

const { data, isLoading } = useEntityList("domestic-instruments", {
  page,
  pageSize,
  jurisdiction: jurisdictionCode,
});

const sanitize = (v: unknown) =>
  v == null || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    title: sanitize(item.titleInEnglish || item.officialTitle),
    abbreviation: sanitize(item.abbreviation),
    date: formatDate(sanitize(item.date)) || "",
    coldId: sanitize(item.coldId),
  })),
);

const columns = [
  { id: "title", accessorKey: "title", header: "Name" },
  { id: "abbreviation", accessorKey: "abbreviation", header: "Abbreviation" },
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

.instrument-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.instrument-table :deep(th),
.instrument-table :deep(td) {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.instrument-table :deep(th:first-child),
.instrument-table :deep(td:first-child) {
  width: 60%;
}

.instrument-table :deep(th:nth-child(2)),
.instrument-table :deep(td:nth-child(2)) {
  width: auto;
}

.instrument-table :deep(th:nth-child(3)),
.instrument-table :deep(td:nth-child(3)) {
  width: 130px;
  min-width: 130px;
  max-width: 130px;
}

.instrument-table :deep(th:last-child),
.instrument-table :deep(td:last-child) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  padding-right: 16px;
  text-align: right;
}

.instrument-table :deep(tbody tr) {
  height: 72px;
}
.instrument-table :deep(tbody td) {
  height: 72px;
  vertical-align: middle;
}

.instrument-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.instrument-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.instrument-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.instrument-table :deep(thead th span),
.instrument-table :deep(thead th button),
.instrument-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.instrument-table :deep(thead th button:hover),
.instrument-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.instrument-table :deep(thead th button:hover span),
.instrument-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
