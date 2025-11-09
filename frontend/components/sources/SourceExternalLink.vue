<template>
  <div v-if="sourceUrl" class="flex-shrink-0">
    <a
      v-if="sourceUrl"
      :href="sourceUrl as string"
      target="_blank"
      rel="noopener noreferrer"
      class="label inline-flex items-center gap-1 text-cold-teal"
      @click.stop
    >
      <span>{{ label }}</span>
      <UIcon name="i-material-symbols:open-in-new" class="h-4 w-4" />
    </a>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sourceUrl?: string | null | unknown;
  label?: string;
}

withDefaults(defineProps<Props>(), {
  sourceUrl: undefined,
  label: "Link",
});
</script>
