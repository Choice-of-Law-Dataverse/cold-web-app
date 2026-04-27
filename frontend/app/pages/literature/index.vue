<template>
  <BaseDetailLayout
    table="Literature"
    page-heading="Literature"
    :loading="isLoading"
    :data="resultData"
  >
    <template #full-width>
      <GradientTopBorder />
      <div class="w-full px-6 py-6">
        <EntityListFilters
          v-model:theme="selectedTheme"
          :filters="['theme']"
          :count="data?.total"
          :loading="isFetching"
        />

        <EntityListTable
          v-model:page="page"
          v-model:order-by="orderBy"
          v-model:order-dir="orderDir"
          :columns="columns"
          :rows="rows"
          link-base="/literature"
          :total="data?.total"
          :loading="isFetching"
        >
          <template #cell-title="{ row }">
            <span class="result-value-small entity-list__cell">
              {{ row.title || "—" }}
              <img
                v-if="row.openAccess"
                src="https://assets.cold.global/assets/Open_Access_logo_PLoS_transparent.svg"
                alt="Open Access"
                class="ml-1 inline-block h-4 w-4 shrink-0 object-contain align-middle"
              />
            </span>
          </template>
        </EntityListTable>
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
import { sanitizeCell } from "@/utils/format";

useHead({
  title: "Literature — CoLD",
});

const page = ref(1);
const resultData = null;

const selectedTheme = ref<string | undefined>(undefined);
const orderBy = ref<string | undefined>(undefined);
const orderDir = ref<"asc" | "desc" | undefined>(undefined);

watch(selectedTheme, () => {
  page.value = 1;
});

const { data, isLoading, isFetching } = useEntityList("literature", {
  page,
  theme: selectedTheme,
  orderBy,
  orderDir,
});

const rows = computed(() =>
  (data.value?.items ?? []).map((item) => ({
    title: sanitizeCell(item.title),
    author: sanitizeCell(item.author),
    publicationYear: sanitizeCell(item.publicationYear),
    openAccess: Boolean(item.oupJdChapter),
    coldId: sanitizeCell(item.coldId),
  })),
);

const columns: EntityListColumn[] = [
  { key: "title", header: "Title", width: "50%", sortable: true },
  { key: "author", header: "Author(s)", sortable: true },
  {
    key: "publicationYear",
    header: "Year",
    width: "120px",
    sortable: true,
    align: "right",
  },
];
</script>
