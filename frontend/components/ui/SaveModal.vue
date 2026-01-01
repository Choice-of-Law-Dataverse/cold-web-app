<template>
  <UModal
    v-model="modelValueProxy"
    prevent-close
    :ui="{
      container: 'w-screen max-w-none',
      width: 'w-screen max-w-none',
      rounded: 'rounded-none',
    }"
  >
    <div class="p-6">
      <h2 class="mb-4 text-center text-lg font-bold">Ready to submit?</h2>
      <p class="mb-6 text-center">
        Review your submission and add optional comments if needed.
      </p>

      <!-- Comments Field -->
      <UFormGroup size="lg" class="mb-6">
        <template #label>
          <span class="label">Comments</span>
        </template>
        <UTextarea
          v-model="commentsProxy"
          placeholder="Optional comments about your submission"
          class="cold-input mt-2"
          :rows="3"
        />
      </UFormGroup>

      <div class="flex flex-col items-center gap-2">
        <h2
          class="submit-heading mb-4 flex cursor-pointer items-center p-0"
          @click.prevent="handleSubmit()"
        >
          Submit Your Data Now
          <UIcon
            name="i-material-symbols:add-notes-outline"
            class="relative ml-1 inline-block text-[1.2em]"
          />
        </h2>
        <NuxtLink class="gray-link cursor-pointer" @click="closeModal"
          >Go Back</NuxtLink
        >
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { ref, watch } from "vue";
import { z } from "zod";

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  email: { type: String, required: true },
  comments: { type: String, required: true },
  saveModalErrors: { type: Object, required: true },
  name: { type: String, required: true },
  specialists: { type: Array, required: true },
  date: { type: [String, Date], required: false, default: null },
  pdfFile: { type: [Object, null], required: false, default: null },
  instrumentId: {
    type: [String, Number],
    default: null,
  },
  link: { type: String, required: false, default: "" },
  submitterEmail: { type: String, required: false, default: undefined },
  submitterComments: { type: String, required: false, default: undefined },
});
const emit = defineEmits([
  "update:modelValue",
  "update:email",
  "update:comments",
  "update:submitter_email",
  "update:submitter_comments",
  "update:saveModalErrors",
  "update:link",
  "save",
  "update:submitterEmail",
  "update:submitterComments",
]);

const modelValueProxy = ref(props.modelValue);
const emailProxy = ref(props.submitterEmail ?? props.email);
const commentsProxy = ref(props.submitterComments ?? props.comments);
const saveModalErrorsProxy = ref({ ...props.saveModalErrors });
const linkProxy = ref(props.link);

watch(
  () => props.modelValue,
  (val) => {
    modelValueProxy.value = val;
  },
);
watch(modelValueProxy, (val) => {
  emit("update:modelValue", val);
});

watch(
  () => [props.submitterEmail, props.email],
  ([newEmail, legacyEmail]) => {
    emailProxy.value = newEmail ?? legacyEmail;
  },
);
watch(emailProxy, (val) => {
  emit("update:submitterEmail", val);
  emit("update:email", val);
});

watch(
  () => [props.submitterComments, props.comments],
  ([newVal, legacyVal]) => {
    commentsProxy.value = newVal ?? legacyVal;
  },
);
watch(commentsProxy, (val) => {
  emit("update:submitterComments", val);
  emit("update:comments", val);
});

watch(
  () => props.saveModalErrors,
  (val) => {
    saveModalErrorsProxy.value = { ...val };
  },
);
watch(saveModalErrorsProxy, (val) => {
  emit("update:saveModalErrors", val);
});

watch(
  () => props.link,
  (val) => {
    linkProxy.value = val;
  },
);
watch(linkProxy, (val) => {
  emit("update:link", val);
});

const saveModalSchema = z.object({
  submitterComments: z.string().optional(),
});

function validateSaveModal() {
  try {
    const modalData = {
      submitterComments: commentsProxy.value,
    };
    saveModalSchema.parse(modalData);
    saveModalErrorsProxy.value = {};
    return true;
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = {};
      error.errors.forEach((err) => {
        errors[err.path[0]] = err.message;
      });
      saveModalErrorsProxy.value = errors;
    }
    return false;
  }
}

function onSave() {
  emit("save");
}

function closeModal() {
  modelValueProxy.value = false;
}

function handleSubmit() {
  if (validateSaveModal()) {
    onSave();
    closeModal();
  }
}
</script>

<style scoped>
/* Local purple heading for the Submit action */
.submit-heading {
  color: var(--color-cold-purple) !important;
}
</style>
