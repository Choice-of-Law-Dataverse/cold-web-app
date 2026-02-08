<template>
  <UCard class="connect-card h-full w-full" :ui="{ body: '!p-0' }">
    <div v-if="showTopBorder" class="gradient-top-border" />
    <div class="flex h-full flex-col justify-between gap-4 p-4 sm:p-6">
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
        <UButton
          variant="link"
          :to="buttonLink"
          :target="!isRelativeLink && newTab ? '_blank' : undefined"
          :icon="buttonIcon"
          trailing
          :ui="{ base: 'text-base font-semibold' }"
        >
          {{ buttonText }}
        </UButton>
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
@reference "tailwindcss";

.connect-card {
  @apply transition-shadow duration-200;
}

.connect-card:hover {
  @apply shadow-md;
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
</style>
