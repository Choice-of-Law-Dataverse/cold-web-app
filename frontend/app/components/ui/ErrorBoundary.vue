<template>
  <div>
    <!-- For NotFound errors, show the error page -->
    <div v-if="isNotFoundError" class="entity-not-found">
      <div
        class="mx-auto flex min-h-[50vh] flex-col items-center justify-center text-center"
        style="max-width: var(--container-width); width: 100%"
      >
        <h2>{{ error?.message || "Item not found" }}</h2>

        <NuxtLink class="mt-6 cursor-pointer" @click="handleGoBack">
          Go back
        </NuxtLink>
        <NuxtLink class="mt-6 cursor-pointer" @click="handleGoHome">
          Take me back to Home
        </NuxtLink>
      </div>
    </div>
    <!-- For all other cases (no error or non-NotFound errors), show the normal content -->
    <slot v-else />
  </div>
</template>

<script setup lang="ts">
import type { ComponentPublicInstance } from "vue";
import { ref, computed, onErrorCaptured, provide } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "#imports";

interface AppError extends Error {
  statusCode?: number;
  data?: { name?: string };
}

type ErrorHandler = (
  err: Error,
  instance: ComponentPublicInstance | null,
  info: string,
) => void;

const props = defineProps<{
  onError?: ErrorHandler;
  entityType?: string;
}>();

const router = useRouter();
const toast = useToast();

const error = ref<AppError | null>(null);

const isNotFoundError = computed(() => {
  return (
    error.value?.statusCode === 404 ||
    error.value?.data?.name === "NotFoundError" ||
    error.value?.name === "NotFoundError"
  );
});

function retry(): void {
  error.value = null;
}

function handleGoBack(): void {
  error.value = null;
  router.back();
}

function handleGoHome(): void {
  error.value = null;
  router.push("/");
}

onErrorCaptured((err: Error, instance, info) => {
  const appErr = err as AppError;
  const isNotFound =
    appErr.statusCode === 404 ||
    appErr.data?.name === "NotFoundError" ||
    appErr.name === "NotFoundError";

  if (isNotFound) {
    error.value = appErr;
  } else {
    toast.add({
      title: "Error",
      description: err.message || "An unexpected error occurred",
      color: "error",
      duration: 5000,
    });
  }

  if (props.onError) {
    props.onError(err, instance, info);
  }

  return false;
});

provide("errorBoundary", { retry });
</script>
