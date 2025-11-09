<template>
  <USelectMenu
    v-model="selected"
    searchable
    searchable-placeholder="Search a Jurisdiction..."
    class="cold-uselectmenu z-200 w-72 lg:w-96"
    :ui-menu="{ container: 'z-[2050] group', height: 'max-h-96' }"
    :placeholder="placeholder"
    :options="countries"
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
              filter: isCovered(option?.alpha3Code)
                ? undefined
                : 'grayscale(0.9)',
            }"
            class="mr-2 self-center"
            @error="() => handleImageError(erroredAvatars, option?.label)"
          />
        </template>
        <span
          :style="{
            color: isCovered(option?.alpha3Code) ? undefined : 'gray',
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
              filter: isCovered(selected?.alpha3Code)
                ? undefined
                : 'grayscale(0.9)',
            }"
            class="mr-1.5 self-center"
            @error="() => handleImageError(erroredAvatars, selected?.label)"
          />
        </template>
        <span
          class="truncate"
          :style="{
            color: isCovered(selected?.alpha3Code) ? undefined : 'gray',
          }"
        >
          {{ selected?.label }}
        </span>
      </div>
    </template>
  </USelectMenu>
</template>

<script setup>
import { reactive } from "vue";
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
});

const isCovered = (alpha3Code) => {
  if (!alpha3Code || !props.countries) return false;
  const jurisdiction = props.countries.find(
    (j) => j.alpha3Code?.toLowerCase() === alpha3Code?.toLowerCase(),
  );
  return jurisdiction?.answerCoverage > 0;
};

const emit = defineEmits(["countrySelected"]);

const selected = defineModel({
  type: String,
  default: null,
});

const erroredAvatars = reactive({});

const onSelect = (value) => {
  emit("countrySelected", value);
};
</script>
