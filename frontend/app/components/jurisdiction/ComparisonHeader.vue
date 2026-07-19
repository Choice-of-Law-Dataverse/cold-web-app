<template>
  <div class="contents">
    <div
      class="comparison-header-cell sticky top-0 bg-white py-3"
      :class="isScrollable ? 'sticky-col-1' : ''"
    >
      <span class="comparison-header-label">Question</span>
    </div>
    <div
      v-for="(jurisdiction, index) in jurisdictions"
      :key="'h-' + (jurisdiction.coldId || jurisdiction.name)"
      class="comparison-header-cell sticky top-0 bg-white py-3 text-center"
      :class="index === 0 && isScrollable ? 'sticky-col-2' : ''"
      :style="index === 0 && isScrollable ? { left: stickyColLeft } : {}"
    >
      <button
        type="button"
        class="jurisdiction-action-button"
        :class="{ removable: index > 0 }"
        :aria-label="
          index > 0
            ? `Remove ${jurisdiction.name} from comparison`
            : jurisdiction.name
        "
        :disabled="index === 0"
        @click="index > 0 ? removeJurisdiction(jurisdiction.coldId) : null"
      >
        <img
          v-if="jurisdiction.avatar"
          :src="jurisdiction.avatar"
          :alt="`${jurisdiction.name} flag`"
          class="h-3.5 w-5 flex-shrink-0 rounded-sm object-cover"
        />
        <span class="min-w-0 truncate">{{
          jurisdictionLabel(jurisdiction)
        }}</span>
        <UIcon
          v-if="index > 0"
          name="i-heroicons-x-mark-20-solid"
          class="h-4 w-4 flex-shrink-0"
        />
      </button>
    </div>
    <div
      class="comparison-header-cell comparison-header-cell--match sticky top-0 bg-white py-3"
      :class="isScrollable ? 'sticky-col-match' : ''"
      aria-hidden="true"
    />
  </div>
</template>

<script setup lang="ts">
import { inject } from "vue";
import { ComparisonStateKey } from "./comparisonState";

const state = inject(ComparisonStateKey);
if (!state) throw new Error("Comparison state not provided");

const {
  jurisdictions,
  removeJurisdiction,
  isScrollable,
  stickyColLeft,
  jurisdictionLabel,
} = state;
</script>
