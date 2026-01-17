<template>
  <div v-if="loading">
    <LoadingBar class="!mt-8" />
  </div>
  <div v-else>
    <BaseLegalContent
      :title="displayTitle"
      :anchor-id="anchorId"
      :class="props.class"
      :loading="loading"
      :error="error?.message"
    >
      <template #header-actions>
        <div v-if="hasEnglishTranslation" class="flex items-center gap-1">
          <!-- Original label (fades when English is active) -->
          <span
            class="label-key-provision-toggle mr-[-0px]"
            :class="{
              'opacity-25': showEnglish,
              'opacity-100': !showEnglish,
            }"
          >
            Original
          </span>

          <UToggle
            v-model="showEnglish"
            size="2xs"
            class="bg-[var(--color-cold-gray)]"
          />

          <!-- English label (fades when Original is active) -->
          <span
            class="label-key-provision-toggle"
            :class="{
              'opacity-25': !showEnglish,
              'opacity-100': showEnglish,
            }"
          >
            English
          </span>
        </div>
      </template>

      {{ content }}
    </BaseLegalContent>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useLegalProvision } from "@/composables/useLegalProvision";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps<{
  provisionId: string;
  class?: string;
  instrumentTitle?: string;
  table?: "Domestic Legal Provisions" | "Regional Legal Provisions";
}>();

const emit = defineEmits<{
  "update:hasEnglishTranslation": [value: boolean];
}>();

const {
  title,
  content,
  loading,
  error,
  hasEnglishTranslation,
  showEnglish,
  anchorId,
} = useLegalProvision({
  provisionId: props.provisionId,
  onHasEnglishTranslationUpdate: (value) =>
    emit("update:hasEnglishTranslation", value),
  table: props.table,
});

const displayTitle = computed(() => {
  if (loading.value) return "Loading...";
  if (error.value) return "Error";
  const baseTitle = title.value || props.provisionId;
  if (props.instrumentTitle) {
    return `${baseTitle}, ${props.instrumentTitle}`;
  }
  return baseTitle;
});
</script>
