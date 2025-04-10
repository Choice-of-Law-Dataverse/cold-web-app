<template>
  <div>
    <USelectMenu
      class="lg:w-60 cold-uselectmenu"
      :class="{ 'non-all-selected': modelValue.length > 0 }"
      :placeholder="options[0]"
      size="lg"
      :options="options"
      :model-value="modelValue"
      @update:modelValue="handleUpdate"
      searchable
      selected-icon="i-material-symbols:circle"
      multiple
    >
      <template #option="{ option }">
        <div class="flex items-center">
          <UAvatar
            :src="option.avatar || 'https://placehold.co/20x20'"
            size="2xs"
            class="mr-2"
          />
          <span>{{ option.label || option }}</span>
        </div>
      </template>
      <template #label>
        <div
          v-if="modelValue.length"
          class="flex items-center overflow-hidden whitespace-nowrap"
        >
          <template v-for="(selected, index) in modelValue" :key="index">
            <UAvatar
              :src="selected.avatar || 'https://placehold.co/20x20'"
              size="2xs"
              class="mr-1 inline-block"
            />
            <span class="mr-2 inline-block">{{
              selected.label || selected
            }}</span>
          </template>
        </div>
        <span v-else>{{ options[0] }}</span>
      </template>
    </USelectMenu>
  </div>
</template>

<script setup>
//import { ref } from 'vue'

const props = defineProps({
  options: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const handleUpdate = (newValue) => {
  // If the default option is selected, reset to empty array
  if (newValue.includes(props.options[0])) {
    emit('update:modelValue', [])
  } else {
    emit('update:modelValue', newValue)
  }
}
</script>
