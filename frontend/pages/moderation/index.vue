<template>
  <div class="py-12">
    <h1 class="mb-8 text-3xl font-bold">Suggestions Moderation</h1>

    <UCard>
      <div class="flex flex-col gap-4 p-6">
        <NuxtLink
          v-for="category in categories"
          :key="category.id"
          :to="`/moderation/${category.id}`"
          class="text-lg text-blue-600 hover:text-blue-800 hover:underline"
        >
          {{ category.label }}
        </NuxtLink>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { MODERATION_CATEGORIES } from "@/config/moderationConfig";

definePageMeta({
  middleware: ["moderation"],
});

const categories = MODERATION_CATEGORIES;
</script>
