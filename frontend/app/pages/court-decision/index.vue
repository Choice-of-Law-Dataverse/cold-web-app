<template>
  <BaseDetailLayout
    table="Court Decisions"
    page-heading="Court Decisions"
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
          link-base="/court-decision"
          :total="data?.total"
          :loading="isFetching"
        />
      </div>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityListFilters from "@/components/entity-list/EntityListFilters.vue";
import EntityListTable, {
  type EntityListColumn,
} from "@/components/entity-list/EntityListTable.vue";
import GradientTopBorder from "@/components/ui/GradientTopBorder.vue";
import { useEntityList } from "@/composables/useEntityList";
import { formatDate, sanitizeCell } from "@/utils/format";
import type { JurisdictionOption } from "@/types/analyzer";

useHead({
  title: "Court Decisions — CoLD",
});

const route = useRoute();

const page = ref(1);
const resultData = null;

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const selectedTheme = ref<string | undefined>(undefined);
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const jurisdictionCode = computed(
  () => selectedJurisdiction.value?.coldId?.toUpperCase() || "",
);

const caseRank = computed(() => {
  const raw = route.query.caseRank;
  const value = Array.isArray(raw) ? raw[0] : raw;
  return value ? String(value) : undefined;
});

watch([jurisdictionCode, selectedTheme, caseRank], () => {
  page.value = 1;
});

const { data, isLoading, isFetching } = useEntityList("court-decisions", {
  page,
  jurisdiction: jurisdictionCode,
  theme: selectedTheme,
  caseRank,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    caseTitle: sanitizeCell(item.caseTitle),
    caseCitation: sanitizeCell(item.caseCitation),
    date:
      formatDate(sanitizeCell(item.publicationDateIso), {
        monthStyle: "short",
      }) || "",
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "caseTitle", header: "Case Title", width: "50%", sortable: true },
  { key: "caseCitation", header: "Citation", sortable: true },
  {
    key: "date",
    header: "Date",
    width: "140px",
    sortable: "publicationDateIso",
    align: "right",
  },
];
</script>
