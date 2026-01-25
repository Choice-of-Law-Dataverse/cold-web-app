<template>
  <img
    v-if="flagUrl"
    :src="flagUrl"
    :alt="alt"
    :class="[sizeClasses, props.class]"
    :style="{ filter: shouldFade ? 'grayscale(0.9)' : undefined }"
    @error="onImageError"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useCoveredCountries } from "@/composables/useJurisdictions";

const FLAG_BASE_URL = "https://choiceoflaw.blob.core.windows.net/assets/flags/";

type FlagSize = "xs" | "sm" | "md" | "lg";

const props = withDefaults(
  defineProps<{
    /** ISO 3166-1 alpha-3 country code */
    iso3?: string | null;
    /** Size preset for the flag */
    size?: FlagSize;
    /** Custom CSS classes to apply */
    class?: string;
    /** Alt text for the image (defaults to "{iso3} flag") */
    alt?: string;
    /**
     * Controls flag fading behavior:
     * - undefined: Auto-fade based on coverage data (default)
     * - true: Always show faded
     * - false: Never show faded
     */
    faded?: boolean;
  }>(),
  {
    iso3: undefined,
    size: "md",
    class: "",
    alt: undefined,
    faded: undefined,
  },
);

const emit = defineEmits<{
  (event: "error", e: Event): void;
}>();

const { data: coveredCountries } = useCoveredCountries();

const flagUrl = computed(() => {
  if (!props.iso3) return null;
  return `${FLAG_BASE_URL}${props.iso3.toLowerCase()}.svg`;
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case "xs":
      return "w-5 h-auto flex-shrink-0 object-contain";
    case "sm":
      return "w-6 h-auto flex-shrink-0 object-contain";
    case "md":
      return "w-7 h-auto flex-shrink-0 object-contain";
    case "lg":
      return "w-8 h-auto flex-shrink-0 object-contain";
    default:
      return "w-7 h-auto flex-shrink-0 object-contain";
  }
});

const shouldFade = computed(() => {
  // If faded is explicitly set, use that value
  if (props.faded !== undefined) {
    return props.faded;
  }

  // Auto-fade based on coverage data
  if (!props.iso3) return false;
  if (!coveredCountries.value || coveredCountries.value.size === 0) {
    // Coverage data not loaded yet - don't fade
    return false;
  }
  return !coveredCountries.value.has(props.iso3.toLowerCase());
});

const alt = computed(() => {
  return props.alt ?? (props.iso3 ? `${props.iso3} flag` : "Country flag");
});

const onImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  target.style.display = "none";
  emit("error", e);
};
</script>
