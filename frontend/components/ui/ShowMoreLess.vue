<template>
  <div class="mt-[-2px] list-none">
    <button
      v-if="!isExpanded"
      :class="['link-button-night', 'cursor-pointer']"
      @click.prevent="emit('update:isExpanded', true)"
    >
      <Icon name="material-symbols:add" :class="iconClass" />
      Show more {{ label }}
    </button>
    <button
      v-else
      :class="['link-button-night', 'cursor-pointer']"
      @click="emit('update:isExpanded', false)"
    >
      <Icon name="material-symbols:remove" :class="iconClass" />
      Show less {{ label }}
    </button>
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
    default: "link-button-night",
  },
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px]",
  },
});

const emit = defineEmits(["update:isExpanded"]);
</script>
