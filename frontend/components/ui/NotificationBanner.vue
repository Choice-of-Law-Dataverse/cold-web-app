<template>
  <div class="notification-banner result-value-small">
    <UIcon
      name="i-material-symbols:flag-outline"
      size="18"
      class="icon-adjust"
    />
    We don’t have data for {{ jurisdictionName }}.
    <a href="/contact" class="contact-link">Contact us</a> if you want to
    contribute.
  </div>
</template>

<script setup>
defineProps({
  jurisdictionName: {
    type: String,
    required: true,
  },
})
</script>

<style scoped>
.notification-banner {
  @apply bg-[--color-cold-cream] p-4 outline outline-1 outline-[--color-cold-cream];
  margin-bottom: 24px;
}

.icon-adjust {
  @apply translate-y-[3px];
  margin-right: 4px;
}
</style>
