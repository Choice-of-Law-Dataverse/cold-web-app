<template>
  <div v-if="sourceUrl" class="flex-shrink-0">
    <a
      v-if="sourceUrl"
      :href="sourceUrl as string"
      target="_blank"
      rel="noopener noreferrer"
      class="label source-link inline-flex items-center gap-1 text-cold-teal"
      @click.stop
    >
      <template v-if="openAccess">
        <img
          class="h-4 w-4"
          src="https://choiceoflaw.blob.core.windows.net/assets/Open_Access_logo_PLoS_transparent.svg"
          alt="Open Access Logo"
        />
      </template>
      <template v-else>
        <UIcon name="i-material-symbols:open-in-new" class="h-5 w-5" />
      </template>
      <span>{{ label }}</span>
    </a>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sourceUrl?: string | null | unknown;
  label?: string;
  openAccess?: boolean;
}

withDefaults(defineProps<Props>(), {
  sourceUrl: undefined,
  label: "Link",
  openAccess: false,
});
</script>

<style scoped>
.source-link {
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: color-mix(in srgb, var(--color-cold-teal) 8%, transparent);
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.source-link:hover {
  background-color: color-mix(in srgb, var(--color-cold-teal) 15%, transparent);
  transform: translateY(-1px);
}
</style>
