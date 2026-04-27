<template>
  <UCard class="connect-card h-full w-full" :ui="{ body: '!p-0' }">
    <GradientTopBorder v-if="showTopBorder" />
    <div class="flex h-full flex-col justify-between gap-4 p-4 sm:p-6">
      <div>
        <h2 class="card-title" :class="{ 'text-center': centerTitle }">
          {{ title }}
        </h2>
        <p
          v-if="subtitle"
          class="card-subtitle"
          :class="{ 'text-center': centerTitle }"
        >
          {{ subtitle }}
        </p>
      </div>

      <div class="icon-container">
        <NuxtLink
          v-if="isRelativeLink"
          :to="buttonLink"
          :aria-label="buttonText"
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
        </NuxtLink>
        <a
          v-else
          :href="buttonLink"
          :target="newTab ? '_blank' : '_self'"
          :rel="newTab ? 'noopener noreferrer' : ''"
          :aria-label="buttonText"
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

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    buttonText: string;
    buttonLink: string;
    iconName?: string;
    imageSrc?: string;
    newTab?: boolean;
    buttonIcon?: string;
    centerTitle?: boolean;
    showTopBorder?: boolean;
  }>(),
  {
    subtitle: "",
    iconName: "",
    imageSrc: "",
    newTab: true,
    buttonIcon: "",
    centerTitle: true,
    showTopBorder: false,
  },
);

const isRelativeLink = computed(() => {
  return (
    props.buttonLink.startsWith("/") ||
    (!props.buttonLink.includes("://") &&
      !props.buttonLink.startsWith("mailto:"))
  );
});
</script>

<style scoped>
@reference "@/assets/styles.css";

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
    color-mix(in srgb, var(--color-cold-purple) 10%, transparent),
    color-mix(in srgb, var(--color-cold-green) 14%, transparent)
  );
  color: var(--color-cold-purple);
}

.icon-link:hover .icon-wrapper {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 16%, transparent),
    color-mix(in srgb, var(--color-cold-green) 20%, transparent)
  );
  transform: scale(1.05);
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
