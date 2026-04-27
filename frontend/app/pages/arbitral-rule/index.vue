<template>
  <BaseDetailLayout
    table="Arbitral Rules"
    page-heading="Arbitral Rules"
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
          link-base="/arbitral-rule"
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
import { formatDate, sanitizeCell } from "@/utils/format";

useHead({
  title: "Arbitral Rules — CoLD",
});

const page = ref(1);
const resultData = null;
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const { data, isLoading, isFetching } = useEntityList("arbitral-rules", {
  page,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    setOfRules: sanitizeCell(item.setOfRules),
    inForceFrom:
      formatDate(sanitizeCell(item.inForceFrom), { monthStyle: "short" }) || "",
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "setOfRules", header: "Set of Rules", width: "60%", sortable: true },
  {
    key: "inForceFrom",
    header: "In Force From",
    width: "140px",
    sortable: true,
    align: "right",
  },
];
</script>
