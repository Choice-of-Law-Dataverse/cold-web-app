<template>
  <div class="w-full">
    <USelectMenu
      v-model="internalValue"
      class="cold-uselectmenu w-full"
      :class="{
        'non-all-selected': multiple
          ? internalValue?.length > 0
          : !!internalValue,
      }"
      :placeholder="
        props.placeholder ||
        (isObjectOptions ? options?.[0].label : options?.[0])
      "
      size="lg"
      :items="options"
      value-key="label"
      :search-input="{ placeholder: 'Search...' }"
      :multiple="multiple"
      :loading="loading"
    >
      <template #item="{ item }">
        <div class="flex items-center">
          <CountryFlag
            v-if="showAvatars && isObjectOptions && item.alpha3Code"
            :iso3="item.alpha3Code"
            :faded="!isCovered(item.alpha3Code)"
            class="mr-2"
          />
          <span
            :style="{
              color: isCovered(item?.alpha3Code) ? undefined : 'gray',
            }"
          >
            {{ isObjectOptions ? item.label : item }}
          </span>
        </div>
      </template>
      <template #label>
        <!-- Single selection mode -->
        <div v-if="!multiple && internalValue" class="w-full">
          <template v-if="isObjectOptions">
            <div
              v-if="showAvatars"
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <CountryFlag
                v-if="internalValue.alpha3Code"
                :iso3="internalValue.alpha3Code"
                :faded="!isCovered(internalValue.alpha3Code)"
                class="mr-1.5"
              />
              <span
                class="truncate"
                :style="{
                  color: isCovered(internalValue?.alpha3Code)
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
                  color: isCovered(internalValue?.alpha3Code)
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
        <!-- Multiple selection mode -->
        <div v-else-if="multiple && internalValue?.length" class="w-full">
          <template v-if="isObjectOptions">
            <div
              v-if="showAvatars"
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <template v-for="(selected, index) in internalValue" :key="index">
                <CountryFlag
                  v-if="selected.alpha3Code"
                  :iso3="selected.alpha3Code"
                  :faded="!isCovered(selected.alpha3Code)"
                  class="mr-1.5"
                />
                <span
                  class="mr-2 inline-block truncate"
                  :style="{
                    color: isCovered(selected?.alpha3Code) ? undefined : 'gray',
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
                internalValue.map((item) => item.label).join(", ")
              }}</span>
            </div>
          </template>
          <template v-else>
            <div
              class="flex w-full items-center overflow-hidden whitespace-nowrap"
            >
              <span class="truncate">{{ internalValue.join(", ") }}</span>
            </div>
          </template>
        </div>
        <!-- Default placeholder -->
        <span v-else class="truncate">
          {{
            props.placeholder ||
            (isObjectOptions ? options?.[0].label : options?.[0])
          }}
        </span>
      </template>
    </USelectMenu>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import CountryFlag from "@/components/ui/CountryFlag.vue";

const props = defineProps({
  options: { type: Array, required: true },
  modelValue: { type: Array, default: () => [] },
  showAvatars: { type: Boolean, default: false },
  multiple: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
  highlightJurisdictions: { type: Boolean, default: false },
  placeholder: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue"]);

const { data: coveredCountries } = useCoveredCountries();

const isCovered = (alpha3Code) => {
  if (!props.highlightJurisdictions) {
    return true;
  } else {
    if (!alpha3Code) return true;
    if (!coveredCountries.value) return true;
    return coveredCountries.value.has(alpha3Code.toLowerCase());
  }
};

const isObjectOptions = computed(() => typeof props.options?.[0] === "object");

const internalValue = computed({
  get() {
    if (!props.multiple) {
      if (props.modelValue?.length === 0) return null;
      const item = props.modelValue?.[0];
      if (!isObjectOptions.value) {
        return item;
      }
      if (typeof item === "object") {
        return props.options.find((o) => o.label === item.label) || item;
      }
      return props.options.find((o) => o.label === item) || item;
    }

    if (!isObjectOptions.value) {
      return props.modelValue;
    }
    return props.modelValue.map((item) => {
      if (typeof item === "object") {
        return props.options.find((o) => o.label === item.label) || item;
      }
      return props.options.find((o) => o.label === item) || item;
    });
  },
  set(newValue) {
    if (!props.multiple) {
      if (!newValue) {
        emit("update:modelValue", []);
      } else {
        const firstLabel = isObjectOptions.value
          ? props.options?.[0]?.label
          : props.options?.[0];
        const newLabel =
          typeof newValue === "object" ? newValue?.label : newValue;
        if (
          firstLabel &&
          newLabel &&
          firstLabel === newLabel &&
          /^All(\s|\b)/.test(firstLabel)
        ) {
          emit("update:modelValue", []);
          return;
        }
        const processed =
          typeof newValue === "object"
            ? props.options.find((o) => o.label === newValue.label) || newValue
            : props.options.find((o) => o.label === newValue) || newValue;
        emit("update:modelValue", [processed]);
      }
      return;
    }

    if (!isObjectOptions.value) {
      const firstLabel = props.options?.[0];
      if (
        firstLabel &&
        /^All(\s|\b)/.test(firstLabel) &&
        newValue.includes(firstLabel)
      ) {
        emit("update:modelValue", []);
        return;
      }
      emit("update:modelValue", newValue);
    } else {
      const firstLabel = props.options?.[0]?.label;
      const containsAll = newValue.some((val) => {
        const lbl = typeof val === "object" ? val.label : val;
        return (
          firstLabel && lbl === firstLabel && /^All(\s|\b)/.test(firstLabel)
        );
      });
      if (containsAll) {
        emit("update:modelValue", []);
        return;
      }
      const processed = newValue.map((val) => {
        if (typeof val === "object") {
          return props.options.find((o) => o.label === val.label) || val;
        }
        return props.options.find((o) => o.label === val) || val;
      });
      emit("update:modelValue", processed);
    }
  },
});
</script>
