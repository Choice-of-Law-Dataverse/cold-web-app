<template>
  <BaseDetailLayout
    table="Specialists"
    page-heading="Specialists"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="rules-table">
          <UTable :columns="columns" :data="rows">
            <template #specialist-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/specialist/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                  >{{ row.original.specialist }}</span
                >
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.specialist }}</span
              >
            </template>
            <template #affiliation-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/specialist/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.affiliation
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.affiliation
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/specialist/${row.original.coldId}`"
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
import { computed, ref } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityListPagination from "@/components/layout/EntityListPagination.vue";
import { useEntityList } from "@/composables/useEntityList";

useHead({
  title: "Specialists — CoLD",
});

const page = ref(1);
const pageSize = 250;
const resultData = null;

const { data, isLoading } = useEntityList("specialists", { page, pageSize });

const sanitize = (v: unknown) =>
  v == null || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (data.value?.items ?? [])
    .map((item) => ({
      specialist: sanitize(item.specialist),
      affiliation: sanitize(item.affiliation),
      coldId: sanitize(item.coldId),
    }))
    .filter((r) => Boolean(r.specialist)),
);

const columns = [
  { id: "specialist", accessorKey: "specialist", header: "Name" },
  { id: "affiliation", accessorKey: "affiliation", header: "Affiliation" },
  { id: "open", accessorKey: "coldId", header: "" },
];
</script>

<style scoped>
.rules-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.rules-table :deep(th),
.rules-table :deep(td) {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.rules-table :deep(th:first-child),
.rules-table :deep(td:first-child) {
  width: 40%;
}

.rules-table :deep(th:nth-child(2)),
.rules-table :deep(td:nth-child(2)) {
  width: auto;
}

.rules-table :deep(th:last-child),
.rules-table :deep(td:last-child) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  padding-right: 16px;
  text-align: right;
}

.rules-table :deep(td:last-child a.label) {
  font-weight: 600;
  font-size: 12px;
}

.rules-table :deep(tbody tr) {
  height: 72px;
}
.rules-table :deep(tbody td) {
  height: 72px;
  vertical-align: middle;
}

.rules-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.rules-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.rules-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.rules-table :deep(thead th span),
.rules-table :deep(thead th button),
.rules-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.rules-table :deep(thead th button:hover),
.rules-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.rules-table :deep(thead th button:hover span),
.rules-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
