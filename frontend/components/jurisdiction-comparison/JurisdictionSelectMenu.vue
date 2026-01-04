<template>
  <USelectMenu
    v-model="selected"
    searchable
    searchable-placeholder="Search a Jurisdiction..."
    class="cold-uselectmenu z-200 w-72 lg:w-96"
    :ui-menu="{ container: 'z-[2050] group', height: 'max-h-96' }"
    :placeholder="placeholder"
    :options="availableCountries"
    :disabled="disabled"
    size="xl"
    @change="onSelect"
  >
    <!-- Custom option rendering with avatars -->
    <template #option="{ option }">
      <div class="flex items-center">
        <template v-if="option?.avatar && !erroredAvatars?.[option?.label]">
          <UAvatar
            :src="option.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
              filter: option?.answerCoverage > 0 ? undefined : 'grayscale(0.9)',
            }"
            class="mr-2 self-center"
            @error="() => handleImageError(erroredAvatars, option?.label)"
          />
        </template>
        <span
          :style="{
            color: option?.answerCoverage > 0 ? undefined : 'gray',
          }"
        >
          {{ option?.label }}
        </span>
      </div>
    </template>

    <!-- Custom label rendering for selected value -->
    <template #label>
      <div
        v-if="selected"
        class="flex w-full items-center overflow-hidden whitespace-nowrap"
      >
        <template v-if="selected?.avatar && !erroredAvatars?.[selected?.label]">
          <UAvatar
            :src="selected.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
              filter:
                selected?.answerCoverage > 0 ? undefined : 'grayscale(0.9)',
            }"
            class="mr-1.5 self-center"
            @error="() => handleImageError(erroredAvatars, selected?.label)"
          />
        </template>
        <span
          class="truncate"
          :style="{
            color: selected?.answerCoverage > 0 ? undefined : 'gray',
          }"
        >
          {{ selected?.label }}
        </span>
      </div>
    </template>
  </USelectMenu>
</template>

<script setup>
import { reactive, computed } from "vue";
import { handleImageError } from "@/utils/handleImageError";

const props = defineProps({
  countries: {
    type: Array,
    required: true,
  },
  placeholder: {
    type: String,
    default: "Pick a Jurisdiction",
  },
  excludedCodes: {
    type: Array,
    default: () => [],
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const availableCountries = computed(() => {
  if (!props.excludedCodes || props.excludedCodes.length === 0) {
    return props.countries;
  }

  const excludedSet = new Set(
    props.excludedCodes.map((code) => code?.toUpperCase()).filter(Boolean),
  );

  return props.countries.filter(
    (country) => !excludedSet.has(country.alpha3Code?.toUpperCase()),
  );
});

const emit = defineEmits(["country-selected"]);

const selected = defineModel({
  type: String,
  default: null,
});

const erroredAvatars = reactive({});

const onSelect = (value) => {
  emit("country-selected", value);
};
</script>
