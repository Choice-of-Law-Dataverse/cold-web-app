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

<script setup>
defineProps({
  isExpanded: {
    type: Boolean,
    required: true,
  },
  label: {
    type: String,
    default: "",
  },
  buttonClass: {
    type: String,
    default: "link-button",
  },
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px]",
  },
});

const emit = defineEmits(["update:isExpanded"]);
</script>
