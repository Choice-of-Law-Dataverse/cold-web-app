<script setup lang="ts">
import { ref, computed } from "vue";
import { useFeedback } from "@/composables/useFeedback";

const props = defineProps<{
  entityType: string;
  entityId: string;
  entityTitle?: string;
}>();

const user = useUser();
const { isSubmitting, submitFeedback } = useFeedback();

const feedbackType = ref("");
const message = ref("");
const email = ref("");
const popoverOpen = ref(false);
const modalOpen = ref(false);

const feedbackTypeOptions = [
  { label: "Suggest improvement", value: "improve" },
  { label: "Missing data", value: "missing_data" },
  { label: "Wrong information", value: "wrong_info" },
  { label: "Outdated information", value: "outdated" },
  { label: "Other", value: "other" },
];

const userEmail = computed(() => {
  const u = user.value;
  if (!u) return "";
  return ((u as Record<string, unknown>).email as string) || "";
});

if (userEmail.value) {
  email.value = userEmail.value;
}

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
  email.value = userEmail.value;
}

async function handleSubmit() {
  const success = await submitFeedback({
    entity_type: props.entityType,
    entity_id: props.entityId,
    entity_title: props.entityTitle,
    feedback_type: feedbackType.value,
    message: message.value,
    submitter_email: email.value,
  });
  if (success) {
    resetForm();
    popoverOpen.value = false;
    modalOpen.value = false;
  }
}

function openFeedback() {
  if (window.innerWidth >= 1024) {
    popoverOpen.value = true;
  } else {
    modalOpen.value = true;
  }
}
</script>

<template>
  <div class="fixed right-6 bottom-6 z-40">
    <UPopover
      v-model:open="popoverOpen"
      :content="{ side: 'top', align: 'end', sideOffset: 8 }"
      class="hidden lg:block"
    >
      <UButton
        icon="i-material-symbols:rate-review-outline"
        size="xl"
        color="primary"
        class="shadow-lg"
        aria-label="Give feedback"
        @click.stop
      />

      <template #content>
        <div class="w-80 p-4">
          <h3 class="mb-3 text-base font-semibold">Give Feedback</h3>

          <div class="flex flex-col gap-3">
            <UFormField label="Feedback type">
              <USelect
                v-model="feedbackType"
                :items="feedbackTypeOptions"
                placeholder="Select type..."
                class="w-full"
              />
            </UFormField>

            <UFormField label="Message">
              <UTextarea
                v-model="message"
                placeholder="Describe what you'd like to report..."
                :rows="3"
                class="w-full"
              />
            </UFormField>

            <UFormField label="Email">
              <UInput
                v-model="email"
                type="email"
                placeholder="your@email.com"
                class="w-full"
              />
            </UFormField>

            <UButton
              block
              :loading="isSubmitting"
              :disabled="!canSubmit"
              @click="handleSubmit"
            >
              Submit Feedback
            </UButton>
          </div>
        </div>
      </template>
    </UPopover>

    <UButton
      icon="i-material-symbols:rate-review-outline"
      size="xl"
      color="primary"
      class="shadow-lg lg:hidden"
      aria-label="Give feedback"
      @click="openFeedback"
    />

    <UModal v-model:open="modalOpen">
      <template #content>
        <div class="p-6">
          <h3 class="mb-4 text-lg font-semibold">Give Feedback</h3>

          <div class="flex flex-col gap-4">
            <UFormField label="Feedback type">
              <USelect
                v-model="feedbackType"
                :items="feedbackTypeOptions"
                placeholder="Select type..."
                class="w-full"
              />
            </UFormField>

            <UFormField label="Message">
              <UTextarea
                v-model="message"
                placeholder="Describe what you'd like to report..."
                :rows="4"
                class="w-full"
              />
            </UFormField>

            <UFormField label="Email">
              <UInput
                v-model="email"
                type="email"
                placeholder="your@email.com"
                class="w-full"
              />
            </UFormField>

            <div class="flex justify-end gap-2">
              <UButton
                variant="ghost"
                color="neutral"
                @click="modalOpen = false"
              >
                Cancel
              </UButton>
              <UButton
                :loading="isSubmitting"
                :disabled="!canSubmit"
                @click="handleSubmit"
              >
                Submit Feedback
              </UButton>
            </div>
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>
