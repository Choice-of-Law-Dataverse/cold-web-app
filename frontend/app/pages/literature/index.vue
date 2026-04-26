<template>
  <BaseDetailLayout
    table="Literature"
    page-heading="Literature"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <div class="literature-table">
          <UTable :columns="columns" :data="rows">
            <template #title-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/literature/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{ row.original.title }}</span>
                <img
                  v-if="row.original.openAccess"
                  src="https://assets.cold.global/assets/Open_Access_logo_PLoS_transparent.svg"
                  alt="Open Access"
                  class="ml-1 inline-flex w-3"
                />
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.title
              }}</span>
            </template>
            <template #author-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/literature/${row.original.coldId}`"
                class="table-row-link"
              >
                <span
                  class="result-value-small block truncate whitespace-nowrap"
                >
                  {{ row.original.author }}
                </span>
              </NuxtLink>
              <span
                v-else
                class="result-value-small block truncate whitespace-nowrap"
                >{{ row.original.author }}</span
              >
            </template>
            <template #publicationYear-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/literature/${row.original.coldId}`"
                class="table-row-link"
              >
                <span class="result-value-small">{{
                  row.original.publicationYear
                }}</span>
              </NuxtLink>
              <span v-else class="result-value-small">{{
                row.original.publicationYear
              }}</span>
            </template>
            <template #open-cell="{ row }">
              <NuxtLink
                v-if="row.original.coldId"
                :to="`/literature/${row.original.coldId}`"
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
  title: "Literature — CoLD",
});

const page = ref(1);
const pageSize = 200;
const resultData = null;

const { data, isLoading } = useEntityList("literature", {
  page,
  pageSize,
});

const sanitize = (v: unknown) =>
  v == null || v === "NA" ? "" : String(v).trim();

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    title: sanitize(item.title),
    author: sanitize(item.author),
    publicationYear: sanitize(item.publicationYear),
    openAccess: Boolean(item.oupJdChapter),
    coldId: sanitize(item.coldId),
  })),
);

const columns = [
  { id: "title", accessorKey: "title", header: "Title" },
  { id: "author", accessorKey: "author", header: "Author(s)" },
  {
    id: "publicationYear",
    accessorKey: "publicationYear",
    header: "Year",
  },
  { id: "open", accessorKey: "coldId", header: "" },
];
</script>

<style scoped>
.literature-table :deep(table) {
  table-layout: fixed;
  width: 100%;
}

.literature-table :deep(th),
.literature-table :deep(td) {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 16px;
}

.literature-table :deep(th:first-child),
.literature-table :deep(td:first-child) {
  width: 50%;
}

.literature-table :deep(th:nth-child(2)),
.literature-table :deep(td:nth-child(2)) {
  width: auto;
}

.literature-table :deep(th:nth-child(3)),
.literature-table :deep(td:nth-child(3)) {
  width: 120px;
  min-width: 120px;
  max-width: 120px;
}

.literature-table :deep(th:last-child),
.literature-table :deep(td:last-child) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  padding-right: 16px;
  text-align: right;
}

.literature-table :deep(tbody tr) {
  height: 72px;
}
.literature-table :deep(tbody td) {
  height: 72px;
  vertical-align: middle;
}

.literature-table :deep(tbody tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.literature-table :deep(tbody tr:hover .arrow-icon) {
  animation: bounce-right 0.4s ease-out;
}

.literature-table :deep(thead th) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.literature-table :deep(thead th span),
.literature-table :deep(thead th button),
.literature-table :deep(thead th button span) {
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: var(--color-cold-night);
}

.literature-table :deep(thead th button:hover),
.literature-table :deep(thead th a:hover) {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}
.literature-table :deep(thead th button:hover span),
.literature-table :deep(thead th a:hover span) {
  color: inherit;
  text-decoration: none;
}
</style>
