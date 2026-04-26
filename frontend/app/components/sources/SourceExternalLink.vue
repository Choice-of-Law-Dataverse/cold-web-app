<template>
  <div v-if="sourceUrl" class="flex-shrink-0">
    <UButton
      v-if="sourceUrl"
      :to="sourceUrl as string"
      target="_blank"
      rel="noopener noreferrer"
      :aria-label="`${label} (opens in new tab)`"
      variant="ghost"
      color="primary"
      size="xs"
      :icon="openAccess ? undefined : 'i-material-symbols:open-in-new'"
      trailing-icon="i-material-symbols:open-in-new"
      @click.stop
    >
      <template v-if="openAccess" #leading>
        <img
          class="mr-2 h-4 w-4 shrink-0 object-contain opacity-100 transition-[width,margin,opacity] duration-200 group-hover:mr-0 group-hover:w-0 group-hover:opacity-0"
          src="https://choiceoflaw.blob.core.windows.net/assets/Open_Access_logo_PLoS_transparent.svg"
          alt="Open Access Logo"
        />
      </template>
      {{ label }}
    </UButton>
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
