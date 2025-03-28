<template>
  <div>
    <h2>{{ error.statusCode }} Error</h2>
    <h2>{{ error.message }}</h2>
  </div>
</template>

<script setup>
defineProps(['error'])
</script>
