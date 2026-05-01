<script setup lang="ts">
import { ref, computed, watchEffect } from "vue";
import { useFeedback } from "@/composables/useFeedback";
import type { components } from "@/types/api-schema";

type EntityType = components["schemas"]["EntityType"];
type FeedbackType = components["schemas"]["FeedbackType"];

const props = defineProps<{
  entityType: EntityType;
  entityId: string;
  entityTitle?: string;
}>();

const user = useUser();
const { isSubmitting, submitFeedback } = useFeedback();

const feedbackType = ref<FeedbackType | "">("");
const message = ref("");
const email = ref("");
const popoverOpen = ref(false);

const feedbackTypeOptions = [
  { label: "Suggest improvement", value: "improve" },
  { label: "Missing data", value: "missing_data" },
  { label: "Wrong information", value: "wrong_info" },
  { label: "Outdated information", value: "outdated" },
  { label: "Other", value: "other" },
];

const messagePlaceholder = computed(() => {
  switch (feedbackType.value) {
    case "improve":
      return "What would make this better?";
    case "missing_data":
      return "What's missing, and where can we find it?";
    case "wrong_info":
      return "What's wrong, and what's the correct information?";
    case "outdated":
      return "What's changed? Link a current source if you can.";
    case "other":
      return "Tell us what's on your mind…";
    default:
      return "Tell us what's missing, wrong, or could be better…";
  }
});

const userEmail = computed(() => {
  const u = user.value;
  if (!u) return "";
  return ((u as Record<string, unknown>).email as string) || "";
});

watchEffect(() => {
  if (userEmail.value && !email.value) {
    email.value = userEmail.value;
  }
});

const canSubmit = computed(
  () => feedbackType.value && message.value.trim() && email.value.trim(),
);

function resetForm() {
  feedbackType.value = "";
  message.value = "";
  email.value = "";
}

async function handleSubmit() {
  const success = await submitFeedback({
    entityType: props.entityType,
    entityId: props.entityId,
    entityTitle: props.entityTitle,
    feedbackType: feedbackType.value as FeedbackType,
    message: message.value,
    submitterEmail: email.value,
  });
  if (success) {
    resetForm();
    popoverOpen.value = false;
  }
}
</script>

<template>
  <UPopover
    v-model:open="popoverOpen"
    :content="{ side: 'bottom', align: 'end', sideOffset: 8 }"
  >
    <UButton
      variant="ghost"
      color="neutral"
      size="xs"
      leading-icon="i-material-symbols:rate-review-outline"
      trailing-icon="i-material-symbols:rate-review-outline"
      class="meta-btn"
      aria-label="Give feedback"
    >
      Feedback
    </UButton>

    <template #content>
      <form class="feedback-popover" @submit.prevent="handleSubmit">
        <USelect
          v-model="feedbackType"
          :items="feedbackTypeOptions"
          placeholder="What kind of feedback?"
          aria-label="Feedback type"
          class="w-full"
        />

        <UTextarea
          v-model="message"
          :placeholder="messagePlaceholder"
          aria-label="Feedback message"
          :rows="4"
          autoresize
          class="w-full"
        />

        <UInput
          v-model="email"
          type="email"
          placeholder="your@email.com"
          aria-label="Reply email"
          class="w-full"
        />

        <UButton
          type="submit"
          block
          :loading="isSubmitting"
          :disabled="!canSubmit"
        >
          Send
        </UButton>
      </form>
    </template>
  </UPopover>
</template>

<style scoped>
.feedback-popover {
  width: 21rem;
  max-width: calc(100vw - 1rem);
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
