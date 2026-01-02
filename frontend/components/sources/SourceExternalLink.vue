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
      <template v-if="openAccess">
        <img
          class="w-3"
          src="https://choiceoflaw.blob.core.windows.net/assets/Open_Access_logo_PLoS_transparent.svg"
          alt="Open Access Logo"
        />
      </template>
      <template v-else>
        <UIcon name="i-material-symbols:open-in-new" class="h-4 w-4" />
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
