<template>
  <div v-if="loading">
    <LoadingBar class="!mt-8" />
  </div>
  <div v-else>
    <BaseLegalContent
      :title="displayTitle"
      :anchor-id="anchorId"
      :class="class"
      :loading="loading"
      :error="error"
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

<script setup>
import { computed, watch, onMounted, ref } from "vue";
import { useLegalProvision } from "@/composables/useLegalProvision";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps({
  provisionId: { type: String, required: true },
  class: { type: String, default: "" },
  textType: { type: String, required: true },
  instrumentTitle: { type: String, default: "" },
  table: { type: String, default: "Domestic Legal Provisions" }, // add this line
});

const emit = defineEmits(["update:hasEnglishTranslation"]);

const {
  title,
  content,
  loading,
  error,
  hasEnglishTranslation,
  showEnglish,
  anchorId,
  fetchProvisionDetails,
  updateContent,
} = useLegalProvision({
  provisionId: props.provisionId,
  textType: props.textType,
  onHasEnglishTranslationUpdate: (value) =>
    emit("update:hasEnglishTranslation", value),
  table: props.table, // pass the table prop
});

// New reactive property for the English title
const englishTitle = ref("");

// Watch the content and update englishTitle if the key exists
watch(
  content,
  (newVal) => {
    if (newVal && typeof newVal === "object" && newVal["Title (in English)"]) {
      englishTitle.value = newVal["Title (in English)"];
    }
  },
  { immediate: true },
);

// Update displayTitle to include englishTitle and instrumentTitle if available
const displayTitle = computed(() => {
  if (loading.value) return "Loading...";
  if (error.value) return "Error";
  const baseTitle = title.value || props.provisionId;
  let fullTitle = englishTitle.value
    ? `${baseTitle} - ${englishTitle.value}`
    : baseTitle;
  if (props.instrumentTitle) {
    fullTitle += `, ${props.instrumentTitle}`;
  }
  return fullTitle;
});

// Fetch provision details when component is mounted
onMounted(() => {
  fetchProvisionDetails();
});

watch(
  () => props.textType,
  () => {
    fetchProvisionDetails();
  },
);

watch(showEnglish, updateContent);
</script>
