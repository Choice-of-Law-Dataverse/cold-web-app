<template>
  <div class="w-full">
    <USelectMenu
      v-model="internalValue as any"
      class="w-full"
      :ui="filterUi"
      :placeholder="placeholderText"
      size="lg"
      :items="options as any[]"
      value-key="label"
      :search-input="searchable ? { placeholder: 'Search...' } : false"
      :multiple="multiple"
      :loading="loading"
      :content="(!searchable ? { class: 'max-h-none' } : undefined) as any"
    >
      <template #item="{ item }: { item: any }">
        <div class="flex items-center">
          <JurisdictionFlag
            v-if="
              showAvatars &&
              isObjectOptions &&
              isObjectOption(item) &&
              item.alpha3Code
            "
            :iso3="item.alpha3Code"
            :faded="!isCovered(item.alpha3Code)"
            class="mr-2"
          />
          <span
            :style="{
              color: isCovered(
                isObjectOption(item) ? item.alpha3Code : undefined,
              )
                ? undefined
                : 'gray',
            }"
          >
            {{ isObjectOption(item) ? item.label : item }}
          </span>
        </div>
      </template>
      <template #default>
        <div v-if="!multiple && internalValue" class="w-full">
          <template v-if="isObjectOptions && isObjectOption(internalValue)">
            <div
              v-if="showAvatars"
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <JurisdictionFlag
                v-if="internalValue.alpha3Code"
                :iso3="internalValue.alpha3Code"
                :faded="!isCovered(internalValue.alpha3Code)"
                class="mr-1.5"
              />
              <span
                class="truncate"
                :style="{
                  color: isCovered(internalValue.alpha3Code)
                    ? undefined
                    : 'gray',
                }"
              >
                {{ internalValue.label }}
              </span>
            </div>
            <div
              v-else
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <span
                class="truncate"
                :style="{
                  color: isCovered(internalValue.alpha3Code)
                    ? undefined
                    : 'gray',
                }"
              >
                {{ internalValue.label }}
              </span>
            </div>
          </template>
          <template v-else>
            <div
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{ internalValue }}</span>
            </div>
          </template>
        </div>
        <div
          v-else-if="
            multiple && isArrayValue(internalValue) && internalValue.length
          "
          class="w-full"
        >
          <template v-if="isObjectOptions">
            <div
              v-if="showAvatars"
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <template
                v-for="(selected, index) in asObjectArray(internalValue)"
                :key="index"
              >
                <JurisdictionFlag
                  v-if="selected.alpha3Code"
                  :iso3="selected.alpha3Code"
                  :faded="!isCovered(selected.alpha3Code)"
                  class="mr-1.5"
                />
                <span
                  class="mr-2 inline-block truncate"
                  :style="{
                    color: isCovered(selected.alpha3Code) ? undefined : 'gray',
                  }"
                >
                  {{ selected.label }}
                </span>
              </template>
            </div>
            <div
              v-else
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{
                asObjectArray(internalValue)
                  .map((item) => item.label)
                  .join(", ")
              }}</span>
            </div>
          </template>
          <template v-else>
            <div
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{
                asStringArray(internalValue).join(", ")
              }}</span>
            </div>
          </template>
        </div>
        <span v-else class="truncate">
          {{ placeholderText }}
        </span>
      </template>
    </USelectMenu>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

interface FilterObjectOption {
  label: string;
  alpha3Code?: string;
}

type FilterOption = FilterObjectOption | string;

interface SearchFiltersProps {
  options: FilterOption[];
  modelValue?: FilterOption[];
  showAvatars?: boolean;
  multiple?: boolean;
  loading?: boolean;
  highlightJurisdictions?: boolean;
  placeholder?: string;
  searchable?: boolean;
}

const props = withDefaults(defineProps<SearchFiltersProps>(), {
  modelValue: () => [],
  showAvatars: false,
  multiple: true,
  loading: false,
  highlightJurisdictions: false,
  placeholder: "",
  searchable: true,
});

const emit = defineEmits<{
  "update:modelValue": [value: FilterOption[]];
}>();

const { data: coveredCountries } = useCoveredCountries();

function isObjectOption(value: unknown): value is FilterObjectOption {
  return typeof value === "object" && value !== null && "label" in value;
}

function isArrayValue(value: unknown): value is FilterOption[] {
  return Array.isArray(value);
}

function asObjectArray(value: unknown): FilterObjectOption[] {
  return value as FilterObjectOption[];
}

function asStringArray(value: unknown): string[] {
  return value as string[];
}

function isCovered(alpha3Code: string | undefined): boolean {
  if (!props.highlightJurisdictions) {
    return true;
  }
  if (!alpha3Code) return true;
  if (!coveredCountries.value) return true;
  return coveredCountries.value.has(alpha3Code.toLowerCase());
}

const isObjectOptions = computed(() => typeof props.options?.[0] === "object");

const placeholderText = computed((): string => {
  if (props.placeholder) return props.placeholder;
  const firstOption = props.options?.[0];
  if (!firstOption) return "";
  return isObjectOption(firstOption) ? firstOption.label : firstOption;
});

const hasActiveFilter = computed(() =>
  props.multiple
    ? Array.isArray(internalValue.value) && internalValue.value.length > 0
    : !!internalValue.value,
);

const filterUi = computed(() => ({
  base: hasActiveFilter.value
    ? "border-[var(--color-cold-purple)] text-[var(--color-cold-purple)] bg-[var(--gradient-subtle)]"
    : "",
}));

const internalValue = computed({
  get() {
    if (!props.multiple) {
      if (props.modelValue?.length === 0) return null;
      const item = props.modelValue?.[0];
      if (!isObjectOptions.value) {
        return item;
      }
      if (typeof item === "object") {
        return (
          props.options.find(
            (o) =>
              isObjectOption(o) &&
              isObjectOption(item) &&
              o.label === item.label,
          ) || item
        );
      }
      return (
        props.options.find((o) => isObjectOption(o) && o.label === item) || item
      );
    }

    if (!isObjectOptions.value) {
      return props.modelValue;
    }
    return props.modelValue.map((item) => {
      if (typeof item === "object") {
        return (
          props.options.find(
            (o) =>
              isObjectOption(o) &&
              isObjectOption(item) &&
              o.label === item.label,
          ) || item
        );
      }
      return (
        props.options.find((o) => isObjectOption(o) && o.label === item) || item
      );
    });
  },
  set(newValue: FilterOption | FilterOption[] | null) {
    if (!props.multiple) {
      if (!newValue) {
        emit("update:modelValue", []);
      } else {
        const singleValue = newValue as FilterOption;
        const firstOption = props.options?.[0];
        const firstLabel = isObjectOption(firstOption)
          ? firstOption.label
          : firstOption;
        const newLabel = isObjectOption(singleValue)
          ? singleValue.label
          : singleValue;
        if (
          firstLabel &&
          newLabel &&
          firstLabel === newLabel &&
          typeof firstLabel === "string" &&
          /^All(\s|\b)/.test(firstLabel)
        ) {
          emit("update:modelValue", []);
          return;
        }
        const processed = isObjectOption(singleValue)
          ? props.options.find(
              (o) => isObjectOption(o) && o.label === singleValue.label,
            ) || singleValue
          : props.options.find(
              (o) => isObjectOption(o) && o.label === singleValue,
            ) || singleValue;
        emit("update:modelValue", [processed]);
      }
      return;
    }

    if (!Array.isArray(newValue)) return;
    const arrayValue = newValue as FilterOption[];

    if (!isObjectOptions.value) {
      const firstLabel = props.options?.[0];
      if (
        typeof firstLabel === "string" &&
        /^All(\s|\b)/.test(firstLabel) &&
        (arrayValue as string[]).includes(firstLabel)
      ) {
        emit("update:modelValue", []);
        return;
      }
      emit("update:modelValue", arrayValue);
    } else {
      const firstOption = props.options?.[0];
      const firstLabel = isObjectOption(firstOption)
        ? firstOption.label
        : undefined;
      const containsAll = arrayValue.some((val) => {
        const lbl = isObjectOption(val) ? val.label : val;
        return (
          firstLabel && lbl === firstLabel && /^All(\s|\b)/.test(firstLabel)
        );
      });
      if (containsAll) {
        emit("update:modelValue", []);
        return;
      }
      const processed = arrayValue.map((val) => {
        if (isObjectOption(val)) {
          return (
            props.options.find(
              (o) => isObjectOption(o) && o.label === val.label,
            ) || val
          );
        }
        return (
          props.options.find((o) => isObjectOption(o) && o.label === val) || val
        );
      });
      emit("update:modelValue", processed);
    }
  },
});
</script>
