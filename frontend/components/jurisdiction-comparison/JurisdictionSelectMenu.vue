<template>
  <USelectMenu
    searchable
    searchable-placeholder="Search a Jurisdiction..."
    class="w-72 lg:w-96 cold-uselectmenu"
    placeholder="Pick a Jurisdiction"
    :options="countries"
    v-model="selected"
    @change="onSelect"
    size="xl"
  >
    <!-- Custom option rendering with avatars -->
    <template #option="{ option }">
      <div class="flex items-center">
        <template v-if="option.avatar && !erroredAvatars?.[option.label]">
          <UAvatar
            :src="option.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
            }"
            class="mr-2 self-center"
            @error="() => handleImageError(erroredAvatars, option.label)"
          />
        </template>
        <span>{{ option.label }}</span>
      </div>
    </template>

    <!-- Custom label rendering for selected value -->
    <template #label>
      <div
        v-if="selected"
        class="flex items-center w-full overflow-hidden whitespace-nowrap"
      >
        <template v-if="selected.avatar && !erroredAvatars?.[selected.label]">
          <UAvatar
            :src="selected.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
            }"
            class="mr-1.5 self-center"
            @error="() => handleImageError(erroredAvatars, selected.label)"
          />
        </template>
        <span class="truncate">{{ selected.label }}</span>
      </div>
    </template>
  </USelectMenu>
</template>

<script setup>
import { reactive } from 'vue'
import { handleImageError } from '@/utils/handleImageError'

// Props for the country options
defineProps({
  countries: {
    type: Array,
    required: true,
  },
})

// Emit selection back to the parent
const emit = defineEmits(['countrySelected'])

const selected = defineModel() // v-model integration

// Reactive object for errored avatars
const erroredAvatars = reactive({})

const onSelect = (value) => {
  emit('countrySelected', value) // Emit the selected value
}
</script>
