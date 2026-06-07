<template>
  <USelectMenu
    v-model="internalSelected"
    :search-input="{ placeholder: 'Search a Jurisdiction...' }"
    class="z-200 w-full"
    :placeholder="placeholder"
    :items="selectItems"
    :disabled="disabled"
    size="xl"
    :ui="{
      content:
        'max-h-(--reka-combobox-content-available-height) w-max min-w-(--reka-combobox-trigger-width)',
    }"
  >
    <template #item="{ item }">
      <div class="flex items-center">
        <JurisdictionFlag
          v-if="item.original?.coldId"
          :iso3="item.original.coldId"
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

    <template #default>
      <span
        v-if="internalSelected?.original?.coldId"
        class="flex w-full items-center overflow-hidden whitespace-nowrap"
      >
        <JurisdictionFlag
          :iso3="internalSelected.original.coldId"
          :faded="!hasCoverage(internalSelected.original.answerCoverage)"
          class="mr-1.5 !h-4 !w-auto"
        />
        <span class="truncate">{{ internalSelected.label }}</span>
      </span>
      <span v-else class="truncate text-(--ui-text-muted)">
        {{ placeholder }}
      </span>
    </template>
  </USelectMenu>
</template>

<script setup lang="ts">
import { computed } from "vue";
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
    const code = jurisdiction.coldId;
    return !code || !excludedSet.has(code.toUpperCase());
  });
});

const selectItems = computed<SelectItem[]>(() => {
  return availableJurisdictions.value.map((jurisdiction) => ({
    label: jurisdiction.label,
    value: jurisdiction.coldId || jurisdiction.name,
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

const internalSelected = computed<SelectItem | undefined>({
  get() {
    if (!props.modelValue) {
      return undefined;
    }
    return selectItems.value.find(
      (item) =>
        item.original.coldId === props.modelValue?.coldId ||
        item.original.name === props.modelValue?.name,
    );
  },
  set(value) {
    const jurisdiction = value?.original;
    emit("update:modelValue", jurisdiction);
    emit("jurisdiction-selected", jurisdiction);
  },
});
</script>
