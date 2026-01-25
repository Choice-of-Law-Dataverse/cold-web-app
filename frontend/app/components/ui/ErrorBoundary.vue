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

const isNotFoundError = computed(() => {
  return (
    error.value?.statusCode === 404 ||
    error.value?.data?.name === "NotFoundError" ||
    error.value?.name === "NotFoundError"
  );
});

const retry = () => {
  error.value = null;
};

const handleGoBack = () => {
  error.value = null;
  router.back();
};

const handleGoHome = () => {
  error.value = null;
  router.push("/");
};

onErrorCaptured((err, instance, info) => {
  const isNotFound =
    err?.statusCode === 404 ||
    err?.data?.name === "NotFoundError" ||
    err?.name === "NotFoundError";

  if (isNotFound) {
    error.value = err;
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
