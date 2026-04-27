<template>
  <BaseDetailLayout
    table="Arbitral Awards"
    page-heading="Arbitral Awards"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <GradientTopBorder />
      <div class="w-full px-6 py-6">
        <EntityListFilters
          v-model:jurisdiction="selectedJurisdiction"
          v-model:theme="selectedTheme"
          :filters="['jurisdiction', 'theme']"
          :count="data?.total"
          :loading="isFetching"
        />

        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/arbitral-award"
          :total="data?.total"
          :loading="isFetching"
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
import GradientTopBorder from "@/components/ui/GradientTopBorder.vue";
import { useEntityList } from "@/composables/useEntityList";
import { sanitizeCell } from "@/utils/format";
import type { JurisdictionOption } from "@/types/analyzer";

useHead({
  title: "Arbitral Awards — CoLD",
});

const page = ref(1);
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const selectedTheme = ref<string | undefined>(undefined);
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

watch([jurisdictionCode, selectedTheme], () => {
  page.value = 1;
});

const { data, isLoading, isFetching } = useEntityList("arbitral-awards", {
  page,
  jurisdiction: jurisdictionCode,
  theme: selectedTheme,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    caseNumber: sanitizeCell(item.caseNumber),
    year: sanitizeCell(item.year),
    seatTown: sanitizeCell(item.seatTown),
    source: sanitizeCell(item.source),
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "caseNumber", header: "Case Number", width: "20%", sortable: true },
  { key: "seatTown", header: "Seat (Town)", width: "20%", sortable: true },
  { key: "source", header: "Source", sortable: true },
  {
    key: "year",
    header: "Year",
    width: "100px",
    sortable: true,
    align: "right",
  },
];
</script>
