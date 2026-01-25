<template>
  <div class="section-header mb-6">
    <h2 class="section-title">
      <Icon v-if="icon" :name="icon" class="section-icon" />
      {{ title }}
    </h2>
    <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  icon?: string;
}>();
</script>

<style scoped>
.section-header {
  text-align: center;
}

.section-title {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-cold-night);
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.section-icon {
  font-size: 1.5rem;
  color: var(--color-cold-purple);
}

.section-subtitle {
  font-size: 1rem;
  color: var(--color-cold-night-alpha);
  line-height: 1.5;
}
</style>
