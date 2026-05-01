<template>
  <div class="-mt-0.5 list-none">
    <button
      v-if="!isExpanded"
      aria-expanded="false"
      :class="linkButtonClass"
      @click.prevent="emit('update:isExpanded', true)"
    >
      <Icon name="material-symbols:add" :class="iconClass" />
      Show more {{ label }}
    </button>
    <button
      v-else
      aria-expanded="true"
      :class="linkButtonClass"
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
    iconClass?: string;
  }>(),
  {
    label: "",
    iconClass: "text-base translate-y-[3px]",
  },
);

const emit = defineEmits<{
  "update:isExpanded": [value: boolean];
}>();

const linkButtonClass =
  "text-cold-night hover:text-[color-mix(in_srgb,var(--color-cold-purple)_85%,#000)] cursor-pointer p-0 text-sm font-normal leading-[1.6] no-underline transition-colors duration-200";
</script>
