<template>
  <div class="mb-12">
    <UButton
      variant="link"
      icon="i-material-symbols:arrow-back"
      :trailing="false"
      class="suggestion-button"
      @click="goBack"
    >
      Back
    </UButton>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

function goBack() {
  router.back(); // Takes the user to the previous page
}
</script>
