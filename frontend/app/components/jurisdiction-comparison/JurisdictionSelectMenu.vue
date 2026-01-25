<template>
  <USelectMenu
    v-model="internalSelected"
    :search-input="{ placeholder: 'Search a Jurisdiction...' }"
    class="cold-uselectmenu z-200 w-72 lg:w-96"
    :placeholder="placeholder"
    :items="selectItems"
    :disabled="disabled"
    size="xl"
    @update:model-value="onInternalSelect"
  >
    <!-- Custom item rendering with avatars -->
    <template #item="{ item }">
      <div class="flex items-center">
        <template v-if="item.avatar?.src">
          <img
            :src="item.avatar.src"
            :style="{
              borderRadius: '0',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
              filter: item.hasCoverage ? undefined : 'grayscale(0.9)',
            }"
            class="mr-2 self-center"
          />
        </template>
        <span
          :style="{
            color: item.hasCoverage ? undefined : 'gray',
          }"
        >
          {{ item.label }}
        </span>
      </div>
    </template>

    <!-- Custom label rendering for selected value -->
    <template #leading>
      <template v-if="internalSelected?.avatar?.src">
        <img
          :src="internalSelected.avatar.src"
          :style="{
            borderRadius: '0',
            boxSizing: 'border-box',
            width: 'auto',
            height: '16px',
            filter: hasCoverage(internalSelected?.original?.answerCoverage)
              ? undefined
              : 'grayscale(0.9)',
          }"
          class="mr-1.5 self-center"
        />
      </template>
    </template>
  </USelectMenu>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { JurisdictionOption } from "@/types/analyzer";

interface SelectItem {
  label: string;
  value: string;
  avatar?: { src: string };
  hasCoverage: boolean;
  original: JurisdictionOption;
}

const props = withDefaults(
  defineProps<{
    countries: JurisdictionOption[];
    placeholder?: string;
    excludedCodes?: Array<string | null | undefined>;
    disabled?: boolean;
    modelValue?: JurisdictionOption;
  }>(),
  {
    placeholder: "Pick a Jurisdiction",
    excludedCodes: () => [],
    disabled: false,
    modelValue: undefined,
  },
);

const availableCountries = computed(() => {
  if (!props.excludedCodes.length) {
    return props.countries;
  }

  const excludedSet = new Set(
    props.excludedCodes
      .map((code) => code?.toUpperCase())
      .filter((code): code is string => Boolean(code)),
  );

  return props.countries.filter((country) => {
    const code = country.alpha3Code;
    return !code || !excludedSet.has(code.toUpperCase());
  });
});

const selectItems = computed<SelectItem[]>(() => {
  return availableCountries.value.map((country) => ({
    label: country.label,
    value: country.alpha3Code || country.Name,
    avatar: country.avatar ? { src: country.avatar } : undefined,
    hasCoverage: hasCoverage(country.answerCoverage),
    original: country,
  }));
});

const emit = defineEmits<{
  (
    event: "country-selected" | "update:modelValue",
    value: JurisdictionOption | undefined,
  ): void;
}>();

const internalSelected = ref<SelectItem | undefined>(undefined);

// Sync external modelValue to internal state
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      const found = selectItems.value.find(
        (item) =>
          item.original.alpha3Code === newVal.alpha3Code ||
          item.original.Name === newVal.Name,
      );
      internalSelected.value = found;
    } else {
      internalSelected.value = undefined;
    }
  },
  { immediate: true },
);

const onInternalSelect = (value: SelectItem | undefined) => {
  const jurisdiction = value?.original;
  emit("update:modelValue", jurisdiction);
  emit("country-selected", jurisdiction);
};

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;
</script>
