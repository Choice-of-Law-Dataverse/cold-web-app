<template>
  <div class="w-full">
    <div
      :class="[
        'border-cold-gray relative border-y transition-opacity duration-150',
        props.loading && 'pointer-events-none opacity-50',
      ]"
      :style="widthVars"
    >
      <UTable :columns="utableColumns" :data="props.rows" :ui="utableUi">
        <template
          v-for="col in props.columns"
          #[`${col.key}-cell`]="{ row }"
          :key="col.key"
        >
          <component
            :is="row.original.coldId ? 'a' : 'span'"
            :href="
              row.original.coldId ? rowHref(row.original.coldId) : undefined
            "
            class="table-row-link"
            :class="row.original.coldId ? '' : 'text-gray-400'"
            @click="
              row.original.coldId && handleRowClick($event, row.original.coldId)
            "
          >
            <slot :name="`cell-${col.key}`" :row="row.original" :column="col">
              <span
                class="text-cold-night block overflow-hidden text-sm font-medium text-ellipsis whitespace-nowrap"
              >
                {{ row.original[col.key] || "—" }}
              </span>
            </slot>
          </component>
        </template>

        <template #open-cell="{ row }">
          <a
            v-if="row.original.coldId"
            :href="rowHref(row.original.coldId)"
            class="table-row-link flex h-full items-center justify-end pr-1"
            aria-label="Open"
            @click="handleRowClick($event, row.original.coldId)"
          >
            <UIcon
              :name="ICON_OPEN"
              class="text-cold-night-alpha group-hover/row:text-cold-purple text-xl transition-colors group-hover/row:animate-[bounce-right_0.4s_ease-out]"
            />
          </a>
          <span v-else class="text-gray-400">—</span>
        </template>

        <template #empty>
          <span v-if="!props.loading">
            {{ props.emptyMessage ?? "No results match the selected filters." }}
          </span>
        </template>
      </UTable>
    </div>

    <EntityListPagination
      v-if="props.total && props.pageSize && props.total > props.pageSize"
      :page="page ?? 1"
      :total="props.total"
      :page-size="props.pageSize"
      @update:page="page = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, h, resolveComponent, type CSSProperties } from "vue";
import EntityListPagination from "@/components/layout/EntityListPagination.vue";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import { getEntityConfig } from "@/config/entityRegistry";

export interface EntityListColumn {
  key: string;
  header: string;
  width?: string;
  sortable?: boolean | string;
  align?: "left" | "right";
}

const ICON_OPEN = "i-material-symbols:arrow-forward";
const ICON_SORT_NONE = "i-material-symbols:unfold-more";
const ICON_SORT_ASC = "i-material-symbols:arrow-upward-rounded";
const ICON_SORT_DESC = "i-material-symbols:arrow-downward-rounded";

const COL_WIDTH_CLASSES =
  "[&_th:nth-child(1):not(:last-child)]:w-[var(--el-col-1-w,auto)] [&_td:nth-child(1):not(:last-child)]:w-[var(--el-col-1-w,auto)] " +
  "[&_th:nth-child(2):not(:last-child)]:w-[var(--el-col-2-w,auto)] [&_td:nth-child(2):not(:last-child)]:w-[var(--el-col-2-w,auto)] " +
  "[&_th:nth-child(3):not(:last-child)]:w-[var(--el-col-3-w,auto)] [&_td:nth-child(3):not(:last-child)]:w-[var(--el-col-3-w,auto)] " +
  "[&_th:nth-child(4):not(:last-child)]:w-[var(--el-col-4-w,auto)] [&_td:nth-child(4):not(:last-child)]:w-[var(--el-col-4-w,auto)] " +
  "[&_th:nth-child(5):not(:last-child)]:w-[var(--el-col-5-w,auto)] [&_td:nth-child(5):not(:last-child)]:w-[var(--el-col-5-w,auto)]";

const OPEN_COL_CLASSES =
  "[&_th:last-child]:w-16 [&_th:last-child]:min-w-16 [&_th:last-child]:max-w-16 [&_th:last-child]:pr-3 [&_th:last-child]:text-right " +
  "[&_td:last-child]:w-16 [&_td:last-child]:min-w-16 [&_td:last-child]:max-w-16 [&_td:last-child]:pr-3 [&_td:last-child]:text-right";

const SORT_BTN_CLASSES =
  "px-1.5 py-1 -ml-1.5 rounded text-[11px] font-bold uppercase tracking-[0.06em] text-cold-night-alpha hover:bg-cold-purple-alpha hover:text-cold-night";

const props = withDefaults(
  defineProps<{
    columns: EntityListColumn[];
    rows: Array<{ coldId?: string } & Record<string, unknown>>;
    linkBase: string;
    total?: number;
    pageSize?: number;
    loading?: boolean;
    emptyMessage?: string;
  }>(),
  { pageSize: 100 },
);

const page = defineModel<number>("page");
const orderBy = defineModel<string | undefined>("orderBy");
const orderDir = defineModel<"asc" | "desc" | undefined>("orderDir");

const UButton = resolveComponent("UButton");

const { openDrawer } = useEntityDrawer();

const rowHref = (coldId: string) => `${props.linkBase}/${coldId}`;

const handleRowClick = (event: MouseEvent, coldId: string) => {
  if (event.metaKey || event.ctrlKey || event.shiftKey) return;
  const config = getEntityConfig(props.linkBase);
  if (!config) return;
  event.preventDefault();
  openDrawer(coldId, config.table, props.linkBase);
};

const orderField = (col: EntityListColumn) =>
  typeof col.sortable === "string" ? col.sortable : col.key;

const toggleSort = (col: EntityListColumn) => {
  const field = orderField(col);
  if (orderBy.value !== field) {
    orderBy.value = field;
    orderDir.value = "asc";
  } else {
    orderDir.value = orderDir.value === "asc" ? "desc" : "asc";
  }
  page.value = 1;
};

const sortIcon = (col: EntityListColumn) => {
  if (orderBy.value !== orderField(col)) return ICON_SORT_NONE;
  return orderDir.value === "asc" ? ICON_SORT_ASC : ICON_SORT_DESC;
};

const utableColumns = computed(() => {
  const cols = props.columns.map((col) => {
    const meta =
      col.align === "right"
        ? { class: { th: "text-right", td: "text-right" } }
        : undefined;
    if (!col.sortable) {
      return {
        id: col.key,
        accessorKey: col.key,
        header: col.header,
        meta,
      };
    }
    return {
      id: col.key,
      accessorKey: col.key,
      header: () =>
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          size: "xs",
          label: col.header,
          trailingIcon: sortIcon(col),
          class: [
            SORT_BTN_CLASSES,
            orderBy.value === orderField(col) && "text-cold-night",
          ],
          onClick: () => toggleSort(col),
        }),
      meta,
    };
  });
  cols.push({
    id: "open",
    accessorKey: "coldId",
    header: "",
    meta: undefined,
  });
  return cols;
});

const utableUi = {
  base: `table-fixed w-full ${COL_WIDTH_CLASSES} ${OPEN_COL_CLASSES}`,
  thead: "border-b border-cold-gray",
  th: "overflow-hidden text-ellipsis whitespace-nowrap py-3.5 text-[11px] font-bold uppercase tracking-[0.06em] text-cold-night-alpha",
  tbody:
    "divide-cold-gray-alpha [&>tr]:h-16 [&>tr]:cursor-pointer [&>tr]:transition-colors [&>tr]:hover:bg-[image:var(--gradient-row-hover)]",
  tr: "group/row",
  td: "overflow-hidden text-ellipsis whitespace-nowrap h-16 align-middle",
  empty: "py-12 px-6 text-center text-sm text-cold-night-alpha",
};

const widthVars = computed<CSSProperties>(() => {
  const vars: Record<string, string> = {};
  props.columns.forEach((col, idx) => {
    if (col.width) vars[`--el-col-${idx + 1}-w`] = col.width;
  });
  return vars as CSSProperties;
});
</script>
