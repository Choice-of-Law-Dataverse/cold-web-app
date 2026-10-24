<template>
  <UModal v-model:open="open" :dismissible="false" title="Ready to submit?">
    <template #content>
      <div class="p-6">
        <h2 class="mb-4 text-center text-lg font-bold">Ready to submit?</h2>
        <p class="mb-6 text-center">
          Review your submission and add optional comments if needed.
        </p>

        <UFormField size="lg" class="mb-6">
          <template #label>
            <span class="label">Comments</span>
          </template>
          <UTextarea
            v-model="comments"
            placeholder="Optional comments about your submission"
            class="mt-2"
            :rows="3"
            :disabled="submitting"
          />
        </UFormField>

        <UAlert
          v-if="error"
          color="error"
          variant="soft"
          :title="error"
          icon="i-material-symbols:error"
          class="mb-6"
          data-testid="save-modal-error"
        />

        <div class="flex flex-col items-center gap-2">
          <button
            type="button"
            class="mb-4 flex cursor-pointer items-center p-0 font-bold text-[var(--color-cold-purple)] disabled:cursor-wait disabled:opacity-60"
            :disabled="submitting"
            data-testid="save-modal-submit"
            @click="emit('submit')"
          >
            {{ submitting ? "Submitting…" : "Submit Your Data Now" }}
            <UIcon
              name="i-material-symbols:add-notes-outline"
              class="relative ml-1 inline-block text-[1.2em]"
            />
          </button>
          <button
            type="button"
            class="gray-link cursor-pointer"
            :disabled="submitting"
            @click="open = false"
          >
            Go Back
          </button>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
/**
 * Confirmation step of a suggestion form. It only collects comments and asks
 * the parent to submit; the parent owns the request and closes the modal
 * once it succeeds, so a failure stays visible here.
 */
const open = defineModel<boolean>("open", { required: true });
const comments = defineModel<string>("comments", { default: "" });

withDefaults(
  defineProps<{
    submitting?: boolean;
    error?: string;
  }>(),
  { submitting: false, error: "" },
);

const emit = defineEmits<{
  submit: [];
}>();
</script>
