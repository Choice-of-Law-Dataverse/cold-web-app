<template>
  <div class="mt-12 flex-1">
    <div
      class="flex min-h-[50vh] w-full flex-col items-center justify-center text-center"
    >
      <h2>{{ confirmationMessage }}</h2>

      <div class="mt-6 flex flex-col gap-2">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to">
          {{ link.text }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useHead } from "#imports";

useHead({
  title: "Confirmed — CoLD",
});

interface ConfirmationLink {
  text: string;
  to: string;
}

const route = useRoute();
const confirmationMessage = String(
  route.query.message || "We have received your submission.",
);

let links: ConfirmationLink[] = [{ text: "Take me back to Home", to: "/" }];
if (route.query.links) {
  try {
    const parsed = JSON.parse(String(route.query.links));
    if (Array.isArray(parsed)) {
      links = parsed.filter((l: ConfirmationLink) => l && l.text && l.to);
    }
  } catch {
    /* noop */
  }
}
</script>
