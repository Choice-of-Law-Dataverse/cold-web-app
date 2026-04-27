<template>
  <BaseDetailLayout
    table="Arbitral Institutions"
    page-heading="Arbitral Institutions"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <GradientTopBorder />
      <div class="w-full px-6 py-6">
        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/arbitral-institution"
          :total="data?.total"
          :loading="isFetching"
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
import { sanitizeCell } from "@/utils/format";

useHead({
  title: "Arbitral Institutions — CoLD",
});

const page = ref(1);
const resultData = null;
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const { data, isLoading, isFetching } = useEntityList("arbitral-institutions", {
  page,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    institution: sanitizeCell(item.institution),
    abbreviation: sanitizeCell(item.abbreviation),
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "institution", header: "Institution", width: "60%", sortable: true },
  { key: "abbreviation", header: "Abbreviation", sortable: true },
];
</script>
