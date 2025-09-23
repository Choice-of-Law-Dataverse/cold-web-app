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
        Please provide your contact information to complete your submission.
      </p>

      <!-- Email Field -->
      <UFormGroup
        size="lg"
        :error="saveModalErrorsProxy.submitter_email"
        class="mb-4"
        hint="Required"
      >
        <template #label>
          <span class="label">Email</span>
        </template>
        <UInput
          v-model="emailProxy"
          type="email"
          placeholder="Your email address"
          class="cold-input mt-2"
        />
      </UFormGroup>

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

      <div class="mb-8 w-full">
        <form class="w-full" @submit.prevent="onSubmit">
          <NuxtTurnstile
            ref="turnstile"
            v-model="tokenProxy"
            class="turnstile-full w-full"
            :options="{ size: 'flexible' }"
          />
        </form>
      </div>

      <div class="flex flex-col items-center gap-2">
        <h2
          class="submit-heading mb-4 flex cursor-pointer items-center p-0"
          :aria-disabled="!tokenProxy ? 'true' : 'false'"
          @click.prevent="tokenProxy ? handleSubmit() : null"
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

<script setup lang="ts">
import { ref, watch } from "vue";
import { z } from "zod";

interface Props {
  specialists: Record<string, unknown>[];
  name: string;
  modelValue: boolean;
  email: string;
  comments: string;
  token: string;
  saveModalErrors: Record<string, unknown>;
  date: string | Date;
  pdfFile?: File | null;
  instrumentId?: string | number | null;
  link?: string;
  // New preferred keys for contact info
  submitterEmail?: string;
  submitterComments?: string;
}

const props = withDefaults(defineProps<Props>(), {
  pdfFile: null,
  instrumentId: null,
  link: "",
  submitterEmail: undefined,
  submitterComments: undefined,
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  "update:email": [value: string];
  "update:comments": [value: string];
  "update:submitter_email": [value: string];
  "update:submitter_comments": [value: string];
  "update:token": [value: string];
  "update:saveModalErrors": [value: Record<string, unknown>];
  "update:link": [value: string];
  "save": [];
  "update:submitterEmail": [value: string];
  "update:submitterComments": [value: string];
}>();

const modelValueProxy = ref(props.modelValue);
// Prefer new keys if provided, fallback to legacy
const emailProxy = ref(props.submitterEmail ?? props.email);
const commentsProxy = ref(props.submitterComments ?? props.comments);
const tokenProxy = ref(props.token);
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
  () => props.token,
  (val) => {
    tokenProxy.value = val;
  },
);
watch(tokenProxy, (val) => {
  emit("update:token", val);
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

// Validation schema for SaveModal
const saveModalSchema = z.object({
  submitterEmail: z
    .string()
    .min(1, { message: "Email is required" })
    .email({ message: "Please enter a valid email address" }),
  submitterComments: z.string().optional(),
});

function validateSaveModal() {
  try {
    const modalData = {
      submitterEmail: emailProxy.value,
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
  // Delegate submission to parent (new.vue). Validation was already performed here.
  emit("save");
}

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
  () => props.token,
  (val) => {
    tokenProxy.value = val;
  },
);
watch(tokenProxy, (val) => {
  emit("update:token", val);
});

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
/* Ensure the Cloudflare Turnstile widget spans the full column width */
.turnstile-full {
  display: block;
  width: 100% !important;
}
.turnstile-full :deep(iframe),
.turnstile-full :deep(div),
.turnstile-full :deep(*) {
  max-width: 100% !important;
  width: 100% !important;
}

/* Local purple heading for the Submit action */
.submit-heading {
  color: var(--color-cold-purple) !important;
}
</style>
