<template>
  <div class="list-none mt-[-2px]">
    <NuxtLink
      v-if="!isExpanded"
      @click.prevent="$emit('update:isExpanded', true)"
      class="link-button cursor-pointer"
    >
      <Icon
        name="material-symbols:add"
        class="text-base translate-y-[3px]"
      />
      Show more {{ label }}
    </NuxtLink>
    <NuxtLink
      v-else
      class="link-button cursor-pointer"
      @click="$emit('update:isExpanded', false)"
    >
      <Icon
        name="material-symbols:remove"
        class="text-base translate-y-[3px]"
      />
      Show less {{ label }}
    </NuxtLink>
  </div>
</template>

<script setup>
defineProps({
  isExpanded: {
    type: Boolean,
    required: true
  },
  label: {
    type: String,
    default: ''
  }
})

defineEmits(['update:isExpanded'])
</script> 