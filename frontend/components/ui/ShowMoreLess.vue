<template>
  <div class="list-none mt-[-2px]">
    <NuxtLink
      v-if="!isExpanded"
      @click.prevent="$emit('update:isExpanded', true)"
      :class="[buttonClass, 'cursor-pointer']"
    >
      <Icon name="material-symbols:add" :class="iconClass" />
      Show more {{ label }}
    </NuxtLink>
    <NuxtLink
      v-else
      @click="$emit('update:isExpanded', false)"
      :class="[buttonClass, 'cursor-pointer']"
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
    default: '',
  },
  buttonClass: {
    type: String,
    default: 'link-button',
  },
  iconClass: {
    type: String,
    default: 'text-base translate-y-[3px]',
  },
})

defineEmits(['update:isExpanded'])
</script>
