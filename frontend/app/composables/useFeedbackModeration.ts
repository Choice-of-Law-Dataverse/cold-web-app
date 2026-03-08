import { useApiClient } from "@/composables/useApiClient";
import type { components } from "@/types/api-schema";

type FeedbackPendingItem = components["schemas"]["FeedbackPendingItem"];
type FeedbackDetail = components["schemas"]["FeedbackDetail"];
type FeedbackModerationStatus =
  components["schemas"]["FeedbackModerationStatus"];
type StatusMessage = components["schemas"]["StatusMessage"];

export type { FeedbackPendingItem, FeedbackDetail };

export function useFeedbackModeration() {
  const { client } = useApiClient();

  async function listPending(): Promise<FeedbackPendingItem[]> {
    const { data, error } = await client.GET("/feedback/pending");
    if (error || !data) throw error ?? new Error("Failed to fetch feedback");
    return data;
  }

  async function getDetail(feedbackId: number): Promise<FeedbackDetail> {
    const { data, error } = await client.GET("/feedback/{feedback_id}", {
      params: { path: { feedback_id: feedbackId } },
    });
    if (error || !data)
      throw error ?? new Error("Failed to fetch feedback detail");
    return data;
  }

  async function updateStatus(
    feedbackId: number,
    status: FeedbackModerationStatus,
  ): Promise<StatusMessage> {
    const { data, error } = await client.PATCH("/feedback/{feedback_id}", {
      params: { path: { feedback_id: feedbackId } },
      body: { moderationStatus: status },
    });
    if (error || !data)
      throw error ?? new Error("Failed to update feedback status");
    return data;
  }

  return { listPending, getDetail, updateStatus };
}
