import { ref } from "vue";
import { useApiClient } from "@/composables/useApiClient";
import type { ApiRequestBody } from "~/types/api";

interface FeedbackPayload {
  entity_type: string;
  entity_id: string;
  entity_title?: string;
  feedback_type: string;
  message: string;
  submitter_email: string;
}

interface FeedbackResponse {
  id: number;
}

export function useFeedback() {
  const { apiClient } = useApiClient();
  const isSubmitting = ref(false);
  const toast = useToast();

  async function submitFeedback(payload: FeedbackPayload): Promise<boolean> {
    isSubmitting.value = true;
    try {
      await apiClient<FeedbackResponse>("feedback", {
        method: "POST",
        body: payload as unknown as ApiRequestBody,
      });
      toast.add({
        title: "Feedback submitted",
        description: "Thank you for your feedback!",
        color: "success",
        duration: 4000,
      });
      return true;
    } catch (err: unknown) {
      toast.add({
        title: "Submission failed",
        description:
          err instanceof Error ? err.message : "Please try again later.",
        color: "error",
        duration: 4000,
      });
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  return { isSubmitting, submitFeedback };
}
