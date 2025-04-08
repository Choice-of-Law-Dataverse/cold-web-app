<template>
  <div class="space-y-2 mt-4 mb-3">
    <USkeleton
      class="h-2 rounded-none"
      :style="{
        backgroundColor: 'var(--color-cold-gray-alpha)',
        width: randomWidth,
      }"
    />
  </div>
</template>

<script>
export default {
  name: 'LoadingBar',
  data() {
    return {
      randomWidth: `${Math.floor(Math.random() * (350 - 200 + 1)) + 200}px`, // random width between 200px and 350px
    }
  },
}
</script>
