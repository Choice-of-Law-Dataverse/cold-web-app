<template>
  <UCard
    :class="[
      'cold-ucard connect-card h-full w-full',
      { 'gradient-top-border': showTopBorder },
    ]"
  >
    <div class="flex h-full flex-col justify-between gap-4">
      <div>
        <h2 class="card-title" :class="{ 'text-center': centerTitle }">
          {{ title }}
        </h2>
        <p v-if="subtitle" class="card-subtitle">
          {{ subtitle }}
        </p>
      </div>

      <div class="icon-container">
        <NuxtLink v-if="isRelativeLink" :to="buttonLink" class="icon-link">
          <template v-if="imageSrc">
            <img :src="imageSrc" alt="" class="icon-image" />
          </template>
          <template v-else>
            <div class="icon-wrapper">
              <Icon :name="iconName" size="64" />
            </div>
          </template>
        </NuxtLink>
        <a
          v-else
          :href="buttonLink"
          :target="newTab ? '_blank' : '_self'"
          :rel="newTab ? 'noopener noreferrer' : ''"
          class="icon-link"
        >
          <template v-if="imageSrc">
            <img :src="imageSrc" alt="" class="icon-image" />
          </template>
          <template v-else>
            <div class="icon-wrapper">
              <Icon :name="iconName" size="64" />
            </div>
          </template>
        </a>
      </div>

      <div class="link-container">
        <NuxtLink v-if="isRelativeLink" :to="buttonLink">
          <UButton
            class="connect-button"
            variant="link"
            :icon="buttonIcon"
            trailing
          >
            {{ buttonText }}
          </UButton>
        </NuxtLink>
        <a
          v-else
          :href="buttonLink"
          :target="newTab ? '_blank' : '_self'"
          :rel="newTab ? 'noopener noreferrer' : ''"
        >
          <UButton
            class="connect-button"
            variant="link"
            :icon="buttonIcon"
            trailing
          >
            {{ buttonText }}
          </UButton>
        </a>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: false,
    default: "",
  },
  buttonText: {
    type: String,
    required: true,
  },
  buttonLink: {
    type: String,
    required: true,
  },
  iconName: {
    type: String,
    required: false,
    default: "",
  },
  imageSrc: {
    type: String,
    required: false,
    default: "",
  },
  newTab: {
    type: Boolean,
    default: true,
  },
  buttonIcon: {
    type: String,
    required: false,
    default: "",
  },
  centerTitle: {
    type: Boolean,
    default: true,
  },
  showTopBorder: {
    type: Boolean,
    default: false,
  },
});

const isRelativeLink = computed(() => {
  return (
    props.buttonLink.startsWith("/") ||
    (!props.buttonLink.includes("://") &&
      !props.buttonLink.startsWith("mailto:"))
  );
});
</script>

<style scoped>
.connect-card {
  @apply transition-shadow duration-200;
}

.connect-card:hover {
  @apply shadow-md;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.card-subtitle {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-cold-night-alpha);
}

.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  min-height: 100px;
}

.icon-link {
  display: block;
}

.icon-wrapper {
  @apply inline-flex rounded-2xl p-5 transition-all duration-200;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-green) 8%, transparent),
    color-mix(in srgb, var(--color-cold-teal) 6%, transparent)
  );
  color: var(--color-cold-green);
}

.icon-link:hover .icon-wrapper {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-green) 12%, transparent),
    color-mix(in srgb, var(--color-cold-teal) 10%, transparent)
  );
}

.icon-image {
  height: 5rem;
  max-width: 100%;
  display: block;
}

.link-container {
  display: flex;
  justify-content: center;
  margin-top: auto;
}

.connect-button {
  color: var(--color-cold-purple) !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  transition: color 0.2s ease;
  padding: 0.5rem !important;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.connect-button:hover {
  color: color-mix(in srgb, var(--color-cold-purple) 85%, #000) !important;
}
</style>
