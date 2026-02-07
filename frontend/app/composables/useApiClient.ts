import {
  ApiError,
  NotFoundError,
  createApiError,
  createNotFoundError,
} from "@/types/errors";
import type { ApiRequestBody } from "~/types/api";

/**
 * Shared API client hook for TanStack Query composables
 * Provides configured fetch function that uses server-side proxy for secure API calls
 */
export function useApiClient() {
  const config = useRuntimeConfig();

  const apiClient = async <T>(
    endpoint: string,
    options: {
      body?: ApiRequestBody;
      method?: string;
      timeout?: number;
      headers?: Record<string, string>;
      responseType?: "json" | "text";
    } = {},
  ): Promise<T> => {
    const {
      body,
      method = "POST",
      timeout = 30000,
      responseType = "json",
      ...otherOptions
    } = options;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const fetchOptions = {
        method,
        headers: {
          "Content-Type": "application/json",
          ...otherOptions.headers,
        },
        signal: controller.signal,
        body: body ? JSON.stringify(body) : undefined,
        ...otherOptions,
      };

      const proxiedPath = `/api/proxy/${endpoint.replace(/^\/+/, "")}`;

      let url = proxiedPath;
      if (typeof window === "undefined") {
        const baseUrl = config.public.siteUrl;
        url = `${baseUrl}${proxiedPath}`;
      }

      const response = await fetch(url, fetchOptions);

      if (!response.ok) {
        if (response.status === 404) {
          throw createNotFoundError(
            endpoint,
            method,
            body,
            new Error(`HTTP ${response.status}: ${response.statusText}`),
          );
        }

        throw createApiError(
          endpoint,
          method,
          body,
          new Error(`HTTP ${response.status}: ${response.statusText}`),
        );
      }

      const data =
        responseType === "text" ? await response.text() : await response.json();

      if (responseType === "json" && (data as { error?: string })?.error) {
        const errorMessage = (data as { error: string }).error.toLowerCase();
        if (
          errorMessage.includes("not found") ||
          errorMessage.includes("no entry found")
        ) {
          throw createNotFoundError(
            endpoint,
            method,
            body,
            new Error((data as { error: string }).error),
          );
        }

        throw createApiError(
          endpoint,
          method,
          body,
          new Error((data as { error: string }).error),
        );
      }

      return data;
    } catch (err) {
      if (err instanceof ApiError || err instanceof NotFoundError) {
        throw err;
      }

      if (err instanceof Error && err.name === "AbortError") {
        throw createApiError(
          endpoint,
          method,
          body,
          err,
          "Request timed out. Please try again.",
        );
      }

      throw createApiError(endpoint, method, body, err);
    } finally {
      clearTimeout(timeoutId);
    }
  };

  return { apiClient };
}
