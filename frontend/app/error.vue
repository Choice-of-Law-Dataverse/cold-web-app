<template>
  <div class="bg-cold-bg flex min-h-screen flex-col">
    <Nav />

    <main class="mt-12 flex-1 px-6">
      <div
        class="max-w-container mx-auto flex min-h-[50vh] w-full flex-col items-center justify-center text-center"
      >
        <h2>{{ heading }}</h2>
        <p v-if="detail" class="text-cold-night-alpha mt-2 text-sm">
          {{ detail }}
        </p>

        <div class="mt-6 flex flex-col items-center gap-3">
          <a v-if="isAuthFailure" href="/auth/login" class="text-cold-teal">
            Try logging in again
          </a>
          <NuxtLink to="/" class="text-cold-teal">
            Take me back to Home
          </NuxtLink>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import type { NuxtError } from "#app";
import { computed } from "vue";
import { useRoute } from "vue-router";
import Nav from "@/components/layout/Nav.vue";
import Footer from "@/components/layout/Footer.vue";

const props = defineProps<{ error: NuxtError }>();
const route = useRoute();

const isAuthFailure = computed(() => route.path?.startsWith("/auth/") ?? false);

const heading = computed(() => {
  const code = props.error?.statusCode;
  if (code === 404) {
    return "Sorry, we can’t find the page you’re looking for.";
  }
  if (isAuthFailure.value) {
    return "We couldn’t complete your sign-in.";
  }
  return "Something went wrong.";
});

const detail = computed(() => {
  const code = props.error?.statusCode;
  const status = props.error?.statusMessage;
  const message = props.error?.message;
  const parts = [
    code ? String(code) : null,
    status && status !== "Server Error" ? status : null,
    message && message !== status ? message : null,
  ].filter(Boolean);
  return parts.length > 0 ? parts.join(" — ") : null;
});
</script>
