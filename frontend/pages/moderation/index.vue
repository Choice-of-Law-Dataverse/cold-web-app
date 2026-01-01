<template>
  <div class="container mx-auto max-w-4xl px-6 py-12">
    <h1 class="mb-8 text-3xl font-bold">Suggestions Moderation</h1>

    <div class="space-y-4">
      <UCard
        v-for="category in categories"
        :key="category.id"
        class="cursor-pointer transition-shadow hover:shadow-lg"
        @click="navigateTo(`/moderation/${category.id}`)"
      >
        <template #header>
          <h2 class="text-xl font-semibold">{{ category.label }}</h2>
        </template>
        <p class="text-gray-600">
          Review and approve {{ category.label.toLowerCase() }} submissions
        </p>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MODERATION_CATEGORIES } from "@/config/moderationConfig";

definePageMeta({
  middleware: ["moderation"],
});

const categories = MODERATION_CATEGORIES;
</script>
