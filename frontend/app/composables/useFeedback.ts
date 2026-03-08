import { ref } from "vue";
import { useApiClient } from "@/composables/useApiClient";
import type { components } from "@/types/api-schema";

type FeedbackPayload = components["schemas"]["FeedbackSubmit"];

export function useFeedback() {
  const { client } = useApiClient();
  const isSubmitting = ref(false);
  const toast = useToast();

  async function submitFeedback(payload: FeedbackPayload): Promise<boolean> {
    isSubmitting.value = true;
    try {
      const { error } = await client.POST("/feedback", {
        body: payload,
      });
      if (error) throw error;
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
