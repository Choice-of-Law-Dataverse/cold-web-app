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
        <template v-if="option?.avatar">
          <UAvatar
            :src="option.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
              filter: hasCoverage(option?.answerCoverage)
                ? undefined
                : 'grayscale(0.9)',
            }"
            class="mr-2 self-center"
          />
        </template>
        <span
          :style="{
            color: hasCoverage(option?.answerCoverage) ? undefined : 'gray',
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
        <template v-if="selected?.avatar">
          <UAvatar
            :src="selected.avatar"
            :style="{
              borderRadius: '0',
              border: '1px solid var(--color-cold-gray)',
              boxSizing: 'border-box',
              width: 'auto',
              height: '16px',
              filter: hasCoverage(selected?.answerCoverage)
                ? undefined
                : 'grayscale(0.9)',
            }"
            class="mr-1.5 self-center"
          />
        </template>
        <span
          class="truncate"
          :style="{
            color: hasCoverage(selected?.answerCoverage) ? undefined : 'gray',
          }"
        >
          {{ selected?.label }}
        </span>
      </div>
    </template>
  </USelectMenu>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { JurisdictionOption } from "@/types/analyzer";

const props = withDefaults(
  defineProps<{
    countries: JurisdictionOption[];
    placeholder?: string;
    excludedCodes?: Array<string | null | undefined>;
    disabled?: boolean;
  }>(),
  {
    placeholder: "Pick a Jurisdiction",
    excludedCodes: () => [],
    disabled: false,
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

const emit = defineEmits<{
  (event: "country-selected", value: JurisdictionOption | undefined): void;
}>();

const selected = defineModel<JurisdictionOption | undefined>({
  default: undefined,
});

const onSelect = (value: JurisdictionOption | undefined) => {
  emit("country-selected", value);
};

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;
</script>
