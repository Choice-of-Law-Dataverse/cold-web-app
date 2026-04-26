<template>
  <BaseDetailLayout
    table="Regional Instruments"
    page-heading="Regional Instruments"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <div class="gradient-top-border" />
      <div class="w-full px-6 py-6">
        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/regional-instrument"
          :total="data?.total"
          :loading="isLoading"
        />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityListTable, {
  type EntityListColumn,
} from "@/components/entity-list/EntityListTable.vue";
import { useEntityList } from "@/composables/useEntityList";
import { formatDate, sanitizeCell } from "@/utils/format";

useHead({
  title: "Regional Instruments — CoLD",
});

const page = ref(1);
const resultData = null;
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const { data, isLoading } = useEntityList("regional-instruments", {
  page,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    title: sanitizeCell(item.title),
    abbreviation: sanitizeCell(item.abbreviation),
    date: formatDate(sanitizeCell(item.date), { monthStyle: "short" }) || "",
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "title", header: "Title", width: "60%", sortable: true },
  { key: "abbreviation", header: "Abbreviation", sortable: true },
  {
    key: "date",
    header: "Date",
    width: "140px",
    sortable: true,
    align: "right",
  },
];
</script>
