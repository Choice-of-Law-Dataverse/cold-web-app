<template>
  <div v-if="totalPages > 1" class="entity-pagination">
    <p class="entity-pagination__count">
      <span class="entity-pagination__range"
        >{{ rangeFrom.toLocaleString() }}–{{ rangeTo.toLocaleString() }}</span
      >
      <span class="entity-pagination__sep">of</span>
      <span class="entity-pagination__total">{{ total.toLocaleString() }}</span>
    </p>

    <UPagination
      :page="page"
      :total="total"
      :items-per-page="pageSize"
      :sibling-count="1"
      color="neutral"
      variant="ghost"
      active-color="primary"
      active-variant="solid"
      size="md"
      :ui="paginationUi"
      @update:page="emit('update:page', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  page: number;
  total: number;
  pageSize: number;
}>();

const emit = defineEmits<{ "update:page": [value: number] }>();

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1);

const rangeFrom = computed(() =>
  props.total === 0 ? 0 : (props.page - 1) * props.pageSize + 1,
);
const rangeTo = computed(() =>
  Math.min(props.page * props.pageSize, props.total),
);

const itemBase =
  "entity-pagination__btn inline-flex items-center justify-center !size-9 !min-w-0 !p-0 rounded-md font-medium tabular-nums";

const paginationUi = {
  list: "gap-1",
  item: itemBase,
  first: itemBase,
  prev: itemBase,
  next: itemBase,
  last: itemBase,
  ellipsis: "inline-flex size-9 items-center justify-center text-gray-400",
  label: "text-sm tabular-nums",
};
</script>

<style scoped>
.entity-pagination {
  margin-top: 1.5rem;
  padding: 1rem 0.5rem 0;
  border-top: 1px solid var(--color-cold-gray);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.entity-pagination__count {
  display: inline-flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.8125rem;
  color: var(--color-cold-night-alpha);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.01em;
}

.entity-pagination__range,
.entity-pagination__total {
  color: var(--color-cold-night);
  font-weight: 600;
}

.entity-pagination__sep {
  color: var(--color-cold-night-alpha);
  font-weight: 400;
}

.entity-pagination :deep(.entity-pagination__btn) {
  height: 2.25rem;
  min-width: 2.25rem;
  padding: 0;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0;
  color: var(--color-cold-night);
  background: transparent;
  border: 1px solid transparent;
  transition:
    background-color 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease,
    transform 0.12s ease;
}

.entity-pagination :deep(.entity-pagination__btn:hover) {
  background-color: var(--color-cold-purple-alpha);
  color: var(--color-cold-night);
  border-color: transparent;
}

.entity-pagination :deep(.entity-pagination__btn:active) {
  transform: scale(0.96);
}

.entity-pagination :deep(.entity-pagination__btn:focus-visible) {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
}

.entity-pagination :deep(.entity-pagination__btn:disabled),
.entity-pagination :deep(.entity-pagination__btn[aria-disabled="true"]) {
  color: var(--color-cold-night-alpha);
  opacity: 0.4;
  cursor: not-allowed;
}

.entity-pagination :deep(.entity-pagination__btn[data-state="active"]),
.entity-pagination :deep(.entity-pagination__btn[aria-current="page"]) {
  background-color: var(--color-cold-purple);
  color: white;
  border-color: var(--color-cold-purple);
}

.entity-pagination :deep(.entity-pagination__btn[data-state="active"]:hover),
.entity-pagination :deep(.entity-pagination__btn[aria-current="page"]:hover) {
  background-color: color-mix(
    in srgb,
    var(--color-cold-purple) 85%,
    var(--color-cold-night)
  );
  color: white;
}

.entity-pagination :deep(.entity-pagination__btn .iconify) {
  font-size: 1rem;
}
</style>
