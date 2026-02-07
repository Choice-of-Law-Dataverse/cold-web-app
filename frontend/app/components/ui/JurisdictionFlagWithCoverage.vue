<template>
  <JurisdictionFlag
    :iso3="iso3"
    :size="size"
    :class="props.class"
    :alt="alt"
    :faded="shouldFade"
    @error="(e) => emit('error', e)"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useCoveredCountries } from "@/composables/useJurisdictions";

type FlagSize = "xs" | "sm" | "md" | "lg";

const props = withDefaults(
  defineProps<{
    /** ISO 3166-1 alpha-3 jurisdiction code */
    iso3?: string | null;
    /** Size preset for the flag */
    size?: FlagSize;
    /** Custom CSS classes to apply */
    class?: string;
    /** Alt text for the image */
    alt?: string;
  }>(),
  {
    iso3: undefined,
    size: "md",
    class: "",
    alt: undefined,
  },
);

const emit = defineEmits<{
  (event: "error", e: Event): void;
}>();

const { data: coveredCountries } = useCoveredCountries();

const shouldFade = computed(() => {
  if (!props.iso3) return false;
  if (!coveredCountries.value || coveredCountries.value.size === 0) {
    // Coverage data not loaded yet - don't fade
    return false;
  }
  return !coveredCountries.value.has(props.iso3.toLowerCase());
});
</script>
