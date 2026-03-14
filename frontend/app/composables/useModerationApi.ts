import { useApiClient } from "@/composables/useApiClient";
import type { components } from "@/types/api-schema";

type StatusMessage = components["schemas"]["StatusMessage"];
type PendingSuggestionItem = components["schemas"]["PendingSuggestionItem"];
type SuggestionDetailItem = components["schemas"]["SuggestionDetailItem"];

export type PendingSuggestion = PendingSuggestionItem | SuggestionDetailItem;

export type { StatusMessage as ModerationResponse };

export function useModerationApi() {
  const { client } = useApiClient();

  const listPendingSuggestions = async (
    category: string,
    showAll = false,
  ): Promise<PendingSuggestionItem[]> => {
    const { data, error } = await client.GET(
      "/suggestions/pending/{category}",
      {
        params: {
          path: { category },
          query: showAll ? { show_all: true } : {},
        },
      },
    );
    if (error || !data) throw error ?? new Error("Failed to fetch suggestions");
    return data;
  };

  const getSuggestionDetail = async (
    category: string,
    id: number,
  ): Promise<SuggestionDetailItem> => {
    const { data, error } = await client.GET(
      "/suggestions/{category}/{suggestion_id}",
      {
        params: {
          path: { category, suggestion_id: id },
        },
      },
    );
    if (error || !data) throw error ?? new Error("Failed to fetch suggestion");
    return data;
  };

  const approveSuggestion = async (
    category: string,
    id: number,
  ): Promise<StatusMessage> => {
    const { data, error } = await client.POST(
      "/suggestions/{category}/{suggestion_id}/approve",
      {
        params: {
          path: { category, suggestion_id: id },
        },
      },
    );
    if (error || !data)
      throw error ?? new Error("Failed to approve suggestion");
    return data;
  };

  const rejectSuggestion = async (
    category: string,
    id: number,
  ): Promise<StatusMessage> => {
    const { data, error } = await client.POST(
      "/suggestions/{category}/{suggestion_id}/reject",
      {
        params: {
          path: { category, suggestion_id: id },
        },
      },
    );
    if (error || !data) throw error ?? new Error("Failed to reject suggestion");
    return data;
  };

  const deleteSuggestion = async (
    category: string,
    id: number,
  ): Promise<StatusMessage> => {
    const { data, error } = await client.DELETE(
      "/suggestions/{category}/{suggestion_id}",
      {
        params: {
          path: { category, suggestion_id: id },
        },
      },
    );
    if (error || !data) throw error ?? new Error("Failed to delete suggestion");
    return data;
  };

  return {
    listPendingSuggestions,
    getSuggestionDetail,
    approveSuggestion,
    rejectSuggestion,
    deleteSuggestion,
  };
}
