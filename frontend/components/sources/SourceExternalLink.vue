<template>
  <div v-if="sourceUrl" class="flex-shrink-0">
    <a
      v-if="sourceUrl"
      :href="sourceUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="inline-flex items-center gap-1 text-sm"
      style="color: var(--color-cold-purple)"
      @click.stop
    >
      <UIcon name="i-material-symbols:open-in-new" class="h-4 w-4" />
      <span>{{ label }}</span>
    </a>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sourceUrl?: string | null;
  label?: string;
}

withDefaults(defineProps<Props>(), {
  sourceUrl: null,
  label: "Link",
});
</script>
