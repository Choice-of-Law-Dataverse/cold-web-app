<template>
  <div
    v-if="totalPages > 1"
    class="mt-6 flex items-center justify-between gap-4 px-2"
  >
    <p class="result-value-small text-gray-500">
      Showing {{ rangeFrom }}–{{ rangeTo }} of {{ total }}
    </p>
    <UPagination
      :page="page"
      :total="total"
      :items-per-page="pageSize"
      :sibling-count="1"
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
</script>
