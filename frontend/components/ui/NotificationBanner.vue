<template>
  <div class="notification-banner result-value-small">
    <UIcon
      name="i-material-symbols:flag-outline"
      size="18"
      class="icon-adjust"
    />
    <span v-if="message" v-html="message"></span>
    <template v-else>
      We don’t have data for {{ jurisdictionName }}.
      <a href="/contact" class="contact-link">Contact us</a> if you want to
      contribute.
    </template>
  </div>
</template>

<script setup>
defineProps({
  jurisdictionName: {
    type: String,
    required: false,
  },
  message: {
    type: String,
    required: false,
  },
})
</script>

<style scoped>
.notification-banner {
  background: var(--color-cold-cream);
  padding: 1rem;
  outline: 1px solid var(--color-cold-cream);
  margin-bottom: 24px !important;
}

.icon-adjust {
  transform: translateY(3px);
  margin-right: 4px;
}
</style>
