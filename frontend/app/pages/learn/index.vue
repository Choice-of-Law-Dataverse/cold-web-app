<template>
  <div />
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

onMounted(() => {
  if (route.path === "/learn") {
    router.replace("/learn/open-educational-resources");
  }
});
</script>
