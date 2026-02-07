<template>
  <div />
</template>

<script setup>
import { onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

onMounted(() => {
  if (route.path === "/learn") {
    navigateTo("/learn/open-educational-resources", { replace: true });
  }
});
</script>
