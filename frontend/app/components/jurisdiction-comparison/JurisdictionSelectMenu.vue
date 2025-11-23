<template>
  <USelectMenu
    v-model="selectedValue"
    searchable
    searchable-placeholder="Search a Jurisdiction..."
    :search-input="{ icon: 'i-lucide-search' }"
    class="cold-uselectmenu z-200 w-72 lg:w-96"
    :ui-menu="{ container: 'z-[2050] group', height: 'max-h-96' }"
    :placeholder="placeholder"
    :items="selectItems"
    size="xl"
    label-key="label"
    value-key="value"
  >
    <template #leading="{ modelValue, ui }">
      <div class="flex items-center gap-2 truncate">
        <template v-if="modelValue && selectedItem?.avatar">
          <UAvatar
            :src="selectedItem.avatar"
            :style="avatarStyle(selectedItem.answerCoverage)"
            class="self-center"
            @error="() => handleImageError(erroredAvatars, selectedItem.label)"
          />
          <span class="truncate">{{ selectedItem.label }}</span>
        </template>
        <template v-else>
          <UIcon name="i-lucide-earth" :class="ui.leadingIcon()" />
        </template>
      </div>
    </template>
    <!-- Custom option rendering with avatars -->
    <template #option="{ option }">
      <div class="flex items-center">
        <template v-if="option?.avatar && !erroredAvatars?.[option?.label]">
          <UAvatar
            :src="option.avatar"
            :style="avatarStyle(option?.answerCoverage)"
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
    <template #item-leading="{ item }">
      <span class="size-5 text-center">
        <UAvatar
          v-if="item?.avatar && !erroredAvatars?.[item?.label]"
          :src="item.avatar"
          :style="avatarStyle(item?.answerCoverage)"
          class="self-center"
          @error="() => handleImageError(erroredAvatars, item?.label)"
        />
        <UIcon v-else name="i-lucide-earth" class="text-gray-400" />
      </span>
    </template>

    <template #label>
      <div
        v-if="selectedItem"
        class="flex w-full items-center overflow-hidden whitespace-nowrap"
      >
        <template
          v-if="selectedItem.avatar && !erroredAvatars?.[selectedItem.label]"
        >
          <UAvatar
            :src="selectedItem.avatar"
            :style="avatarStyle(selectedItem.answerCoverage)"
            class="mr-1.5 self-center"
            @error="() => handleImageError(erroredAvatars, selectedItem.label)"
          />
        </template>
        <span
          class="truncate"
          :style="{
            color: selectedItem.answerCoverage > 0 ? undefined : 'gray',
          }"
        >
          {{ selectedItem.label }}
        </span>
      </div>
    </template>
  </USelectMenu>
</template>

<script setup lang="ts">
import { reactive, computed, watch } from "vue";
import { handleImageError } from "@/utils/handleImageError";

const props = defineProps({
  countries: {
    type: Array as PropType<
      Array<{
        label?: string;
        alpha3Code?: string;
        avatar?: string;
        answerCoverage?: number;
      }>
    >,
    required: true,
  },
  placeholder: {
    type: String,
    default: "Pick a Jurisdiction",
  },
  excludedCodes: {
    type: Array as PropType<string[]>,
    default: () => [],
  },
});

const selectItems = computed(() => {
  if (!props.excludedCodes || props.excludedCodes.length === 0) {
    return props.countries.map((country) => ({
      ...country,
      value: country.alpha3Code,
    }));
  }

  const excludedSet = new Set(
    props.excludedCodes.map((code) => code?.toUpperCase()).filter(Boolean),
  );

  return props.countries
    .filter(
      (country) =>
        country.alpha3Code &&
        !excludedSet.has(country.alpha3Code.toUpperCase()),
    )
    .map((country) => ({
      ...country,
      value: country.alpha3Code,
    }));
});

const emit = defineEmits(["countrySelected"]);

const selectedValue = defineModel({
  type: String as PropType<string | null>,
  default: null,
});

const erroredAvatars = reactive({});

const selectedItem = computed(() =>
  selectItems.value.find((item) => item.value === selectedValue.value),
);

const avatarStyle = (coverage?: number) => ({
  borderRadius: "0",
  border: "1px solid var(--color-cold-gray)",
  boxSizing: "border-box",
  width: "auto",
  height: "16px",
  filter: coverage && coverage > 0 ? undefined : "grayscale(0.9)",
});

watch(
  () => selectedValue.value,
  (value) => {
    if (!value) return;
    const match = selectItems.value.find((item) => item.value === value);
    emit("countrySelected", match || null);
  },
);
</script>
