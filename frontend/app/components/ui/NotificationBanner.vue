<template>
  <UAlert :icon="icon" color="neutral" variant="subtle" class="mb-6">
    <template #description>
      <span
        v-if="notificationBannerMessage && notificationBannerMessage.length"
      >
        {{ notificationBannerMessage }}
      </span>
      <span v-else-if="jurisdictionName">
        {{ fallbackMessage.replace("{jurisdiction}", jurisdictionName) }}
        <NuxtLink to="/contact" class="underline hover:opacity-80"
          >Contact us</NuxtLink
        >
        if you want to contribute.
      </span>
      <span v-else>{{ fallbackMessage }}</span>
    </template>
  </UAlert>
</template>

<script setup lang="ts">
defineProps({
  jurisdictionName: {
    type: String,
    required: false,
    default: "",
  },
  notificationBannerMessage: {
    type: String,
    required: false,
    default: "",
  },
  fallbackMessage: {
    type: String,
    required: false,
    default: "We don't have data for {jurisdiction}.",
  },
  icon: {
    type: String,
    required: false,
    default: "i-material-symbols:flag-outline",
  },
});
</script>
