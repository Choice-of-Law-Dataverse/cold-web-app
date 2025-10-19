<template>
  <UCard class="cold-ucard h-full w-full">
    <h2 class="popular-title">{{ title }}</h2>
    <p v-if="subtitle" class="result-value-small" style="text-align: center">
      {{ subtitle }}
    </p>
    <div class="icon-container">
      <NuxtLink v-if="isRelativeLink" :to="buttonLink">
        <template v-if="imageSrc">
          <img :src="imageSrc" alt="" class="h-20 max-w-full" >
        </template>
        <template v-else>
          <Icon :name="iconName" size="72" class="text-cold-green" />
        </template>
      </NuxtLink>
      <a
        v-else
        :href="buttonLink"
        :target="newTab ? '_blank' : '_self'"
        :rel="newTab ? 'noopener noreferrer' : ''"
      >
        <template v-if="imageSrc">
          <img :src="imageSrc" alt="" class="h-20 max-w-full" >
        </template>
        <template v-else>
          <Icon :name="iconName" size="72" class="text-cold-green" />
        </template>
      </a>
    </div>
    <div class="link-container">
      <NuxtLink v-if="isRelativeLink" :to="buttonLink">
        <UButton
          class="suggestion-button"
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
          class="suggestion-button"
          variant="link"
          :icon="buttonIcon"
          trailing
        >
          {{ buttonText }}
        </UButton>
      </a>
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
});

// Check if the link is relative (internal) or absolute (external)
const isRelativeLink = computed(() => {
  return (
    props.buttonLink.startsWith("/") ||
    (!props.buttonLink.includes("://") &&
      !props.buttonLink.startsWith("mailto:"))
  );
});
</script>

<style scoped>
h2 {
  text-align: center;
}

.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 32px;
}

.link-container {
  display: flex;
  justify-content: center;
}

.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
