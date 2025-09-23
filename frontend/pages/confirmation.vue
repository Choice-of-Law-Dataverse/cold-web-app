<template>
  <main class="mt-12 flex-1 px-6">
    <div
      class="mx-auto flex min-h-[50vh] w-full max-w-container flex-col items-center justify-center text-center"
    >
      <h2>{{ confirmationMessage }}</h2>

      <div class="mt-6 flex flex-col gap-2">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to">
          {{ link.text }}
        </NuxtLink>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useRoute } from "vue-router";
import { useHead } from "#imports";

useHead({
  title: "Confirmed — CoLD",
});

const route = useRoute();
const confirmationMessage =
  route.query.message || "We have received your submission.";

let links = [{ text: "Take me back to Home", to: "/" }];
if (route.query.links) {
  try {
    const parsed = JSON.parse(route.query.links);
    if (Array.isArray(parsed)) {
      links = parsed.filter((l) => l && l.text && l.to);
    }
  } catch {
    // ignore, fallback to default
  }
}
</script>

<script>
export default {
  layout: "default",
};
</script>
