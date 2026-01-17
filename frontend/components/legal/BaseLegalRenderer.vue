<template>
  <div>
    <div v-if="hasContent">
      <div v-if="isList" :class="wrapperClass">
        <div
          v-for="(item, index) in items"
          :key="index"
          :class="valueClassMap || defaultClass"
        >
          <slot :item="item" />
        </div>
      </div>
      <div v-else :class="valueClassMap || defaultClass">
        <slot :item="items[0]" />
      </div>
    </div>
    <div v-else-if="displayValue" :class="valueClassMap || defaultClass">
      {{ displayValue }}
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  items: {
    type: [Array, String],
    default: () => [],
  },
  valueClassMap: {
    type: String,
    default: "",
  },
  defaultClass: {
    type: String,
    default: "result-value",
  },
  wrapperClass: {
    type: String,
    default: "flex flex-col gap-1",
  },
  isList: {
    type: Boolean,
    default: true,
  },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: "display",
      fallback: "N/A",
    }),
  },
});

const hasContent = computed(() => {
  if (Array.isArray(props.items)) {
    return props.items.length > 0;
  }
  return props.items && props.items.trim();
});

const displayValue = computed(() => {
  if (hasContent.value) return null;
  if (props.emptyValueBehavior.action === "hide") return null;
  return props.emptyValueBehavior.fallback;
});
</script>
