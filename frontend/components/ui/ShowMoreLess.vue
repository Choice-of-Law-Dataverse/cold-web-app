<template>
  <div class="mt-[-2px] list-none">
    <NuxtLink
      v-if="!isExpanded"
      :class="[buttonClass, 'cursor-pointer']"
      @click.prevent="emit('update:isExpanded', true)"
    >
      <Icon name="material-symbols:add" :class="iconClass" />
      Show more {{ label }}
    </NuxtLink>
    <NuxtLink
      v-else
      :class="[buttonClass, 'cursor-pointer']"
      @click="emit('update:isExpanded', false)"
    >
      <Icon name="material-symbols:remove" :class="iconClass" />
      Show less {{ label }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
interface Props {
  isExpanded: boolean;
  label?: string;
  buttonClass?: string;
  iconClass?: string;
}

withDefaults(defineProps<Props>(), {
  label: "",
  buttonClass: "link-button",
  iconClass: "text-base translate-y-[3px]",
});

const emit = defineEmits<{
  "update:isExpanded": [value: boolean];
}>();
</script>
