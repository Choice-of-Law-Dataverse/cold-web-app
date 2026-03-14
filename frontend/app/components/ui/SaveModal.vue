<template>
  <UModal
    v-model:open="modelValueProxy"
    :dismissible="false"
    title="Ready to submit?"
  >
    <template #content>
      <div class="p-6">
        <h2 class="mb-4 text-center text-lg font-bold">Ready to submit?</h2>
        <p class="mb-6 text-center">
          Review your submission and add optional comments if needed.
        </p>

        <!-- Comments Field -->
        <UFormField size="lg" class="mb-6">
          <template #label>
            <span class="label">Comments</span>
          </template>
          <UTextarea
            v-model="commentsProxy"
            placeholder="Optional comments about your submission"
            class="mt-2"
            :rows="3"
          />
        </UFormField>

        <div class="flex flex-col items-center gap-2">
          <button
            type="button"
            class="mb-4 flex cursor-pointer items-center p-0 font-bold text-[var(--color-cold-purple)]"
            @click="handleSubmit()"
          >
            Submit Your Data Now
            <UIcon
              name="i-material-symbols:add-notes-outline"
              class="relative ml-1 inline-block text-[1.2em]"
            />
          </button>
          <button
            type="button"
            class="gray-link cursor-pointer"
            @click="closeModal"
          >
            Go Back
          </button>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { z } from "zod";

const props = defineProps<{
  modelValue: boolean;
  email: string;
  comments: string;
  saveModalErrors: Record<string, string>;
  name: string;
  specialists?: string[];
  date?: string | Date | null;
  pdfFile?: File | null;
  instrumentId?: string | number | null;
  link?: string;
}>();
const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  "update:email": [value: string];
  "update:comments": [value: string];
  "update:saveModalErrors": [value: Record<string, string>];
  "update:link": [value: string];
  save: [];
}>();

const modelValueProxy = ref(props.modelValue);
const emailProxy = ref(props.email);
const commentsProxy = ref(props.comments);
const saveModalErrorsProxy = ref<Record<string, string>>({
  ...props.saveModalErrors,
});
const linkProxy = ref(props.link ?? "");

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
  () => props.email,
  (val) => {
    emailProxy.value = val;
  },
);
watch(emailProxy, (val) => {
  emit("update:email", val);
});

watch(
  () => props.comments,
  (val) => {
    commentsProxy.value = val;
  },
);
watch(commentsProxy, (val) => {
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
    linkProxy.value = val ?? "";
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
      const errors: Record<string, string> = {};
      error.errors.forEach((err) => {
        const key = err.path[0];
        if (key !== undefined) {
          errors[String(key)] = err.message;
        }
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
