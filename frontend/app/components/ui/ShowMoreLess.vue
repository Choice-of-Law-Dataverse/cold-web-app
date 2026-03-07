<template>
  <div class="mt-[-2px] list-none">
    <button
      v-if="!isExpanded"
      aria-expanded="false"
      :class="['link-button-night', 'cursor-pointer']"
      @click.prevent="emit('update:isExpanded', true)"
    >
      <Icon name="material-symbols:add" :class="iconClass" />
      Show more {{ label }}
    </button>
    <button
      v-else
      aria-expanded="true"
      :class="['link-button-night', 'cursor-pointer']"
      @click="emit('update:isExpanded', false)"
    >
      <Icon name="material-symbols:remove" :class="iconClass" />
      Show less {{ label }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    isExpanded: boolean;
    label?: string;
    buttonClass?: string;
    iconClass?: string;
  }>(),
  {
    label: "",
    buttonClass: "link-button-night",
    iconClass: "text-base translate-y-[3px]",
  },
);

const emit = defineEmits<{
  "update:isExpanded": [value: boolean];
}>();
</script>
