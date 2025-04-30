<template>
  <div>
    <USelectMenu
      class="lg:w-60 cold-uselectmenu"
      :class="{ 'non-all-selected': internalValue.length > 0 }"
      :placeholder="isObjectOptions ? options[0].label : options[0]"
      size="lg"
      :options="options"
      v-model="internalValue"
      :value-key="'label'"
      searchable
      selected-icon="i-material-symbols:circle"
      multiple
    >
      <template #option="{ option }">
        <div class="flex items-center">
          <template
            v-if="
              showAvatars &&
              isObjectOptions &&
              option.avatar &&
              !erroredAvatars[option.label]
            "
          >
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
          <span>{{ isObjectOptions ? option.label : option }}</span>
        </div>
      </template>
      <template #label>
        <div v-if="internalValue.length" class="w-full">
          <template v-if="isObjectOptions">
            <div
              v-if="showAvatars"
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <template v-for="(selected, index) in internalValue" :key="index">
                <UAvatar
                  v-if="selected.avatar && !erroredAvatars[selected.label]"
                  :src="selected.avatar"
                  :style="{
                    borderRadius: '0',
                    border: '1px solid var(--color-cold-gray)',
                    boxSizing: 'border-box',
                    width: 'auto',
                    height: '16px',
                  }"
                  class="mr-1.5 self-center"
                  @error="
                    () => handleImageError(erroredAvatars, selected.label)
                  "
                />
                <span class="mr-2 inline-block truncate">{{
                  selected.label
                }}</span>
              </template>
            </div>
            <div
              v-else
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{
                internalValue.map((item) => item.label).join(', ')
              }}</span>
            </div>
          </template>
          <template v-else>
            <div
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{ internalValue.join(', ') }}</span>
            </div>
          </template>
        </div>
        <span v-else class="truncate">
          {{ isObjectOptions ? options[0].label : options[0] }}
        </span>
      </template>
    </USelectMenu>
  </div>
</template>

<script setup>
const props = defineProps({
  options: { type: Array, required: true },
  modelValue: { type: Array, default: () => [] },
  showAvatars: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

import { computed, reactive } from 'vue'
import { handleImageError } from '../../utils/handleImageError' // new import

// Reactive object for errored avatars
const erroredAvatars = reactive({})

const isObjectOptions = computed(() => typeof props.options[0] === 'object')

// computed wrapper to ensure selected options are the option objects from props.options
const internalValue = computed({
  get() {
    if (!isObjectOptions.value) {
      return props.modelValue
    }
    return props.modelValue.map((item) => {
      if (typeof item === 'object') {
        return props.options.find((o) => o.label === item.label) || item
      }
      return props.options.find((o) => o.label === item) || item
    })
  },
  set(newValue) {
    // If "All…" option is selected, reset the filter by setting newValue to an empty array.
    const allOption = props.options[0]
    const isAllSelected = newValue.some((val) =>
      typeof val === 'object'
        ? val.label === allOption.label
        : val === allOption
    )
    if (isAllSelected) {
      newValue = []
    }
    if (!isObjectOptions.value) {
      emit('update:modelValue', newValue)
    } else {
      const processed = newValue.map((val) => {
        if (typeof val === 'object') {
          return props.options.find((o) => o.label === val.label) || val
        }
        return props.options.find((o) => o.label === val) || val
      })
      emit('update:modelValue', processed)
    }
  },
})
</script>
