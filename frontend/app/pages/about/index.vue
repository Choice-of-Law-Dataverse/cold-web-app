<template>
  <div />
</template>

<script setup>
import { onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

onMounted(() => {
  if (route.path === "/about") {
    navigateTo("/about/about-cold", { replace: true });
  }
});
</script>
