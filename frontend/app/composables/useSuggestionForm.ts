import { ref } from "vue";
import type { z } from "zod";
import { useRouter } from "#imports";
import { useApiClient } from "@/composables/useApiClient";
import type { paths } from "@/types/api-schema";

/** Suggestion endpoints whose body takes `submitter_comments`. */
export type SuggestionEndpoint =
  | "/suggestions/domestic-instruments"
  | "/suggestions/regional-instruments"
  | "/suggestions/international-instruments"
  | "/suggestions/literature";

type SuggestionBody<E extends SuggestionEndpoint> =
  paths[E]["post"]["requestBody"]["content"]["application/json"];

/** Everything a page sends, except the comments the save modal collects. */
export type SuggestionPayload<E extends SuggestionEndpoint> = Omit<
  SuggestionBody<E>,
  "submitter_comments"
>;

export const SUBMISSION_SOURCE = "cold.global";
export const SUBMISSION_FAILED_MESSAGE =
  "There was a problem submitting your suggestion. Please try again.";
export const SUBMISSION_RECEIVED_MESSAGE =
  "Thanks, we have received your submission.";

interface SuggestionFormOptions<E extends SuggestionEndpoint> {
  endpoint: E;
  /** Validates the values returned by `values` before the save modal opens. */
  schema: z.ZodType;
  values: () => unknown;
  payload: () => SuggestionPayload<E>;
}

/**
 * Drives a "suggest a new record" page: validates the form, opens the save
 * modal, posts the suggestion with the modal's comments, and either redirects
 * to the confirmation page or keeps the modal open with an error.
 *
 * Field errors are keyed by the first path segment of each schema issue; the
 * first issue for a field wins, so a "required" check placed before a length
 * check is the message shown for an empty field.
 */
export function useSuggestionForm<E extends SuggestionEndpoint>(
  options: SuggestionFormOptions<E>,
) {
  const router = useRouter();
  const { client } = useApiClient();

  const errors = ref<Record<string, string>>({});
  const comments = ref("");
  const isSaveModalOpen = ref(false);
  const isSubmitting = ref(false);
  const submitError = ref("");

  function validate(): boolean {
    const result = options.schema.safeParse(options.values());
    if (result.success) {
      errors.value = {};
      return true;
    }
    const next: Record<string, string> = {};
    for (const issue of result.error.issues) {
      const field = String(issue.path[0]);
      next[field] ??= issue.message;
    }
    errors.value = next;
    return false;
  }

  function openSaveModal() {
    if (!validate()) return;
    submitError.value = "";
    isSaveModalOpen.value = true;
  }

  async function submit() {
    if (isSubmitting.value) return;
    isSubmitting.value = true;
    submitError.value = "";
    try {
      const body = {
        ...options.payload(),
        submitter_comments: comments.value || undefined,
      };
      const { error } = await client.POST(options.endpoint, {
        body,
        params: { header: { source: SUBMISSION_SOURCE } },
      } as never);
      if (error) throw error;
    } catch {
      submitError.value = SUBMISSION_FAILED_MESSAGE;
      isSubmitting.value = false;
      return;
    }
    isSaveModalOpen.value = false;
    isSubmitting.value = false;
    await router.push({
      path: "/confirmation",
      query: { message: SUBMISSION_RECEIVED_MESSAGE },
    });
  }

  function cancel() {
    return router.push("/");
  }

  return {
    errors,
    comments,
    isSaveModalOpen,
    isSubmitting,
    submitError,
    openSaveModal,
    submit,
    cancel,
  };
}
