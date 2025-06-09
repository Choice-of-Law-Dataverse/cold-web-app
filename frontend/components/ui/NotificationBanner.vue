<template>
  <div class="notification-banner result-value-small">
    <UIcon :name="icon" size="18" class="icon-adjust" />
    <span
      v-if="notificationBannerMessage && notificationBannerMessage.length"
      v-html="notificationBannerMessage"
    ></span>
    <span v-else-if="jurisdictionName">
      {{ fallbackMessage.replace('{jurisdiction}', jurisdictionName) }}
      <a href="/contact" class="contact-link">Contact us</a> if you want to
      contribute.
    </span>
    <span v-else>{{ fallbackMessage }}</span>
  </div>
</template>

<script setup>
defineProps({
  jurisdictionName: {
    type: String,
    required: false,
  },
  notificationBannerMessage: {
    type: String,
    required: false,
    default: '',
  },
  fallbackMessage: {
    type: String,
    required: false,
    default: 'We don’t have data for {jurisdiction}.',
  },
  icon: {
    type: String,
    required: false,
    default: 'i-material-symbols:flag-outline',
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
