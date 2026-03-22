<template>
  <div
    class="section-header"
    :class="{ 'section-header--left': align === 'left' }"
  >
    <h2 class="section-title">
      <Icon v-if="icon" :name="icon" class="section-icon" />
      {{ title }}
    </h2>
    <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    icon?: string;
    align?: "center" | "left";
  }>(),
  { align: "center" },
);
</script>

<style scoped>
.section-header {
  text-align: center;
}

.section-header--left {
  text-align: left;
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
  font-family: "DM Sans", sans-serif;
  color: var(--color-cold-night-alpha);
  line-height: 1.5;
}
</style>
