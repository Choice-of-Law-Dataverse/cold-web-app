<template>
  <USelectMenu
    v-model="internalSelected"
    :search-input="{ placeholder: 'Search a Jurisdiction...' }"
    class="z-200 w-full"
    :placeholder="placeholder"
    :items="selectItems"
    :disabled="disabled"
    size="xl"
    @update:model-value="onInternalSelect"
  >
    <!-- Custom item rendering with avatars -->
    <template #item="{ item }">
      <div class="flex items-center">
        <JurisdictionFlag
          v-if="item.original?.alpha3Code"
          :iso3="item.original.alpha3Code"
          :faded="!item.hasCoverage"
          class="mr-2"
        />
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
      <JurisdictionFlag
        v-if="internalSelected?.original?.alpha3Code"
        :iso3="internalSelected.original.alpha3Code"
        :faded="!hasCoverage(internalSelected?.original?.answerCoverage)"
        class="mr-1.5"
      />
    </template>
  </USelectMenu>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { JurisdictionOption } from "@/types/analyzer";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

interface SelectItem {
  label: string;
  value: string;
  avatar?: { src: string };
  hasCoverage: boolean;
  original: JurisdictionOption;
}

const props = withDefaults(
  defineProps<{
    jurisdictions: JurisdictionOption[];
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

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;

const availableJurisdictions = computed(() => {
  if (!props.excludedCodes.length) {
    return props.jurisdictions;
  }

  const excludedSet = new Set(
    props.excludedCodes
      .map((code) => code?.toUpperCase())
      .filter((code): code is string => Boolean(code)),
  );

  return props.jurisdictions.filter((jurisdiction) => {
    const code = jurisdiction.alpha3Code;
    return !code || !excludedSet.has(code.toUpperCase());
  });
});

const selectItems = computed<SelectItem[]>(() => {
  return availableJurisdictions.value.map((jurisdiction) => ({
    label: jurisdiction.label,
    value: jurisdiction.alpha3Code || jurisdiction.Name,
    avatar: jurisdiction.avatar ? { src: jurisdiction.avatar } : undefined,
    hasCoverage: hasCoverage(jurisdiction.answerCoverage),
    original: jurisdiction,
  }));
});

const emit = defineEmits<{
  (
    event: "jurisdiction-selected" | "update:modelValue",
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
  emit("jurisdiction-selected", jurisdiction);
};
</script>
