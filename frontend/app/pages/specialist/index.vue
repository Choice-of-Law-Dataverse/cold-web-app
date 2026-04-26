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
        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/specialist"
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
import { sanitizeCell } from "@/utils/format";

useHead({
  title: "Specialists — CoLD",
});

const page = ref(1);
const resultData = null;
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

const { data, isLoading } = useEntityList("specialists", {
  page,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? [])
    .map((item) => ({
      specialist: sanitizeCell(item.specialist),
      affiliation: sanitizeCell(item.affiliation),
      coldId: sanitizeCell(item.coldId),
    }))
    .filter((r) => Boolean(r.specialist)),
);

const columns: EntityListColumn[] = [
  { key: "specialist", header: "Name", width: "40%", sortable: true },
  { key: "affiliation", header: "Affiliation", sortable: true },
];
</script>
