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
        <EntityListFilters
          v-model:jurisdiction="selectedJurisdiction"
          :filters="['jurisdiction']"
        />

        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/domestic-instrument"
          :total="data?.total"
          :loading="isLoading"
        />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityListFilters from "@/components/entity-list/EntityListFilters.vue";
import EntityListTable, {
  type EntityListColumn,
} from "@/components/entity-list/EntityListTable.vue";
import { useEntityList } from "@/composables/useEntityList";
import { formatDate, sanitizeCell } from "@/utils/format";
import type { JurisdictionOption } from "@/types/analyzer";

useHead({
  title: "Domestic Instruments — CoLD",
});

const page = ref(1);
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

watch(jurisdictionCode, () => {
  page.value = 1;
});

const { data, isLoading } = useEntityList("domestic-instruments", {
  page,
  jurisdiction: jurisdictionCode,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    title: sanitizeCell(item.titleInEnglish || item.officialTitle),
    abbreviation: sanitizeCell(item.abbreviation),
    date: formatDate(sanitizeCell(item.date), { monthStyle: "short" }) || "",
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "title", header: "Name", width: "60%", sortable: "titleInEnglish" },
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
