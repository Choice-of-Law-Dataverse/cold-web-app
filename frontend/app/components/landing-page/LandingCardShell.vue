<template>
  <UCard class="h-full w-full" :ui="{ body: '!p-0' }">
    <GradientTopBorder />
    <div class="flex w-full flex-col gap-4 p-4 sm:p-6">
      <component
        :is="headerLink ? NuxtLink : 'div'"
        :to="headerLink || undefined"
        :class="headerLink ? 'w-full no-underline' : undefined"
      >
        <h2 :class="['card-title', headerClass]">{{ title }}</h2>
        <p class="card-subtitle">{{ subtitle }}</p>
      </component>

      <div v-if="loading">
        <LoadingLandingPageCard />
      </div>
      <InlineError v-else-if="error" :error="error" />
      <div v-else class="flex w-full flex-col gap-2">
        <slot />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { resolveComponent } from "vue";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import InlineError from "@/components/ui/InlineError.vue";

const NuxtLink = resolveComponent("NuxtLink");

withDefaults(
  defineProps<{
    title: string;
    subtitle: string;
    loading?: boolean;
    error?: Error | null;
    headerLink?: string;
    headerClass?: string;
  }>(),
  {
    loading: false,
    error: null,
    headerLink: undefined,
    headerClass: undefined,
  },
);
</script>
