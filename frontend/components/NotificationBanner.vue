<template>
  <div class="notification-banner result-value-small">
    <UIcon
      name="i-material-symbols:info-outline"
      size="16"
      class="icon-adjust"
    />
    We don’t have a lot of data for this jurisdiction.
    <a href="/contact" class="contact-link">Contact us</a> if you want to
    contribute.
  </div>
</template>

<style scoped>
.notification-banner {
  @apply bg-[--color-cold-cream] p-4 outline outline-1 outline-[--color-cold-cream];
  margin-bottom: 24px;
}

.icon-adjust {
  @apply translate-y-[2px];
  margin-right: 4px;
}
</style>
