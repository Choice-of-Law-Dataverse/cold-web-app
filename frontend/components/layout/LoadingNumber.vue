<template>
  <div class="mb-8 mt-8 flex flex-row space-x-4">
    <USkeleton
      v-for="n in 3"
      :key="n"
      class="h-8 w-8 rounded-full"
      :style="{ backgroundColor: 'var(--color-cold-gray-alpha)' }"
    />
  </div>
</template>
