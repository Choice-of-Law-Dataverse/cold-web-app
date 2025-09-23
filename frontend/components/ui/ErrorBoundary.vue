<template>
  <div>
    <!-- For NotFound errors, show the error page -->
    <div v-if="isNotFoundError" class="entity-not-found">
      <div
        class="mx-auto flex min-h-[50vh] flex-col items-center justify-center text-center"
        style="max-width: var(--container-width); width: 100%"
      >
        <h2>{{ error.message || "Item not found" }}</h2>

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

<script setup>
import { ref, computed, onErrorCaptured, provide } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "#imports";

const props = defineProps({
  onError: {
    type: Function,
    default: undefined,
  },
  entityType: {
    type: String,
    default: "Entity",
  },
});

const router = useRouter();
const toast = useToast();

const error = ref(null);

// Check if error is a NotFoundError
const isNotFoundError = computed(() => {
  return (
    error.value?.statusCode === 404 ||
    error.value?.data?.name === "NotFoundError" ||
    error.value?.name === "NotFoundError"
  );
});

// Error recovery function
const retry = () => {
  error.value = null;
};

// Handle navigation actions with error clearing
const handleGoBack = () => {
  error.value = null;
  router.back();
};

const handleGoHome = () => {
  error.value = null;
  router.push("/");
};

// Capture errors from child components
onErrorCaptured((err, instance, info) => {
  // Check if this is a NotFound error
  const isNotFound =
    err?.statusCode === 404 ||
    err?.data?.name === "NotFoundError" ||
    err?.name === "NotFoundError";

  // For NotFound errors, set the error state to show the error page
  if (isNotFound) {
    error.value = err;
  } else {
    // For non-NotFound errors, show toast and keep content visible
    toast.add({
      title: "Error",
      description: err.message || "An unexpected error occurred",
      color: "red",
      timeout: 5000,
    });
    // Don't set error.value so the content remains visible
  }

  // Call custom error handler if provided
  if (props.onError) {
    props.onError(err, instance, info);
  }

  // Prevent the error from bubbling up
  return false;
});

// Provide retry function to child components
provide("errorBoundary", { retry });
</script>
