<template>
  <div class="w-full">
    <USelectMenu
      class="w-full cold-uselectmenu"
      :class="{
        'non-all-selected': multiple
          ? internalValue?.length > 0
          : !!internalValue,
      }"
      :placeholder="isObjectOptions ? options?.[0].label : options?.[0]"
      size="lg"
      :options="options"
      v-model="internalValue"
      :value-key="'label'"
      searchable
      selected-icon="i-material-symbols:circle"
      :multiple="multiple"
      :loading="loading"
      loadingIcon="i-material-symbols:progress-activity"
      trailing
    >
      <template #option="{ option }">
        <div class="flex items-center">
          <template
            v-if="
              showAvatars &&
              isObjectOptions &&
              option.avatar &&
              !erroredAvatars?.[option.label]
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
        <!-- Single selection mode -->
        <div v-if="!multiple && internalValue" class="w-full">
          <template v-if="isObjectOptions">
            <div
              v-if="showAvatars"
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <UAvatar
                v-if="
                  internalValue.avatar && !erroredAvatars[internalValue.label]
                "
                :src="internalValue.avatar"
                :style="{
                  borderRadius: '0',
                  border: '1px solid var(--color-cold-gray)',
                  boxSizing: 'border-box',
                  width: 'auto',
                  height: '16px',
                }"
                class="mr-1.5 self-center"
                @error="
                  () => handleImageError(erroredAvatars, internalValue.label)
                "
              />
              <span class="truncate">{{ internalValue.label }}</span>
            </div>
            <div
              v-else
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{ internalValue.label }}</span>
            </div>
          </template>
          <template v-else>
            <div
              class="flex items-center w-full overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{ internalValue }}</span>
            </div>
          </template>
        </div>
        <!-- Multiple selection mode -->
        <div v-else-if="multiple && internalValue?.length" class="w-full">
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
        <!-- Default placeholder -->
        <span v-else class="truncate">
          {{ isObjectOptions ? options?.[0].label : options?.[0] }}
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
  multiple: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

import { computed, reactive } from 'vue'
import { handleImageError } from '@/utils/handleImageError'

// Reactive object for errored avatars
const erroredAvatars = reactive({})

const isObjectOptions = computed(() => typeof props.options?.[0] === 'object')

// computed wrapper to ensure selected options are the option objects from props.options
const internalValue = computed({
  get() {
    if (!props.multiple) {
      // Single selection mode - return single value or null
      if (props.modelValue?.length === 0) return null
      const item = props.modelValue?.[0]
      if (!isObjectOptions.value) {
        return item
      }
      if (typeof item === 'object') {
        return props.options.find((o) => o.label === item.label) || item
      }
      return props.options.find((o) => o.label === item) || item
    }

    // Multiple selection mode - return array
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
    if (!props.multiple) {
      // Single selection mode
      if (!newValue) {
        emit('update:modelValue', [])
      } else {
        // If the selected value corresponds to the first "All…" option, clear selection
        const firstLabel = isObjectOptions.value
          ? props.options?.[0]?.label
          : props.options?.[0]
        const newLabel =
          typeof newValue === 'object' ? newValue?.label : newValue
        if (
          firstLabel &&
          newLabel &&
          firstLabel === newLabel &&
          /^All(\s|\b)/.test(firstLabel)
        ) {
          emit('update:modelValue', [])
          return
        }
        const processed =
          typeof newValue === 'object'
            ? props.options.find((o) => o.label === newValue.label) || newValue
            : props.options.find((o) => o.label === newValue) || newValue
        emit('update:modelValue', [processed])
      }
      return
    }

    // Multiple selection mode
    if (!isObjectOptions.value) {
      // If first option (All…) is present in selection, clear to empty (reset)
      const firstLabel = props.options?.[0]
      if (
        firstLabel &&
        /^All(\s|\b)/.test(firstLabel) &&
        newValue.includes(firstLabel)
      ) {
        emit('update:modelValue', [])
        return
      }
      emit('update:modelValue', newValue)
    } else {
      // Object option case
      // Detect if selection contains the first option whose label starts with All…
      const firstLabel = props.options?.[0]?.label
      const containsAll = newValue.some((val) => {
        const lbl = typeof val === 'object' ? val.label : val
        return (
          firstLabel && lbl === firstLabel && /^All(\s|\b)/.test(firstLabel)
        )
      })
      if (containsAll) {
        emit('update:modelValue', [])
        return
      }
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
