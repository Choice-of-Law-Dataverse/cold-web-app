/**
 * Composable for moderation API calls
 * Provides functions to interact with the moderation endpoints
 */

export interface PendingSuggestion {
  id: number;
  created_at: string;
  payload: Record<string, unknown>;
  source?: string;
  token_sub?: string;
  username?: string;
  user_email?: string;
  model?: string;
  case_citation?: string;
  moderation_status?: string;
}

export interface ModerationResponse {
  status: string;
  message: string;
}

export const useModerationApi = () => {
  /**
   * List suggestions for a category
   * @param category - The category to list suggestions for
   * @param showAll - If true, returns all suggestions regardless of status (case-analyzer only)
   */
  const listPendingSuggestions = async (
    category: string,
    showAll = false,
  ): Promise<PendingSuggestion[]> => {
    try {
      const url = showAll
        ? `/api/proxy/suggestions/pending/${category}?show_all=true`
        : `/api/proxy/suggestions/pending/${category}`;

      const { data, error } = await useFetch<PendingSuggestion[]>(url, {
        method: "GET",
      });

      if (error.value) {
        throw new Error(error.value.message || "Failed to fetch suggestions");
      }

      return data.value || [];
    } catch (err) {
      console.error("Error fetching pending suggestions:", err);
      throw err;
    }
  };

  /**
   * Get details for a specific suggestion
   */
  const getSuggestionDetail = async (
    category: string,
    id: number,
  ): Promise<PendingSuggestion> => {
    try {
      const { data, error } = await useFetch<PendingSuggestion>(
        `/api/proxy/suggestions/${category}/${id}`,
        {
          method: "GET",
        },
      );

      if (error.value) {
        throw new Error(error.value.message || "Failed to fetch suggestion");
      }

      if (!data.value) {
        throw new Error("Suggestion not found");
      }

      return data.value;
    } catch (err) {
      console.error("Error fetching suggestion detail:", err);
      throw err;
    }
  };

  /**
   * Approve a suggestion
   */
  const approveSuggestion = async (
    category: string,
    id: number,
  ): Promise<ModerationResponse> => {
    try {
      const { data, error } = await useFetch<ModerationResponse>(
        `/api/proxy/suggestions/${category}/${id}/approve`,
        {
          method: "POST",
        },
      );

      if (error.value) {
        throw new Error(error.value.message || "Failed to approve suggestion");
      }

      return (
        data.value || { status: "success", message: "Suggestion approved" }
      );
    } catch (err) {
      console.error("Error approving suggestion:", err);
      throw err;
    }
  };

  /**
   * Reject a suggestion
   */
  const rejectSuggestion = async (
    category: string,
    id: number,
  ): Promise<ModerationResponse> => {
    try {
      const { data, error } = await useFetch<ModerationResponse>(
        `/api/proxy/suggestions/${category}/${id}/reject`,
        {
          method: "POST",
        },
      );

      if (error.value) {
        throw new Error(error.value.message || "Failed to reject suggestion");
      }

      return (
        data.value || { status: "success", message: "Suggestion rejected" }
      );
    } catch (err) {
      console.error("Error rejecting suggestion:", err);
      throw err;
    }
  };

  /**
   * Delete a suggestion (case-analyzer only)
   */
  const deleteSuggestion = async (
    category: string,
    id: number,
  ): Promise<ModerationResponse> => {
    try {
      const { data, error } = await useFetch<ModerationResponse>(
        `/api/proxy/suggestions/${category}/${id}`,
        {
          method: "DELETE",
        },
      );

      if (error.value) {
        throw new Error(error.value.message || "Failed to delete suggestion");
      }

      return data.value || { status: "success", message: "Suggestion deleted" };
    } catch (err) {
      console.error("Error deleting suggestion:", err);
      throw err;
    }
  };

  return {
    listPendingSuggestions,
    getSuggestionDetail,
    approveSuggestion,
    rejectSuggestion,
    deleteSuggestion,
  };
};
