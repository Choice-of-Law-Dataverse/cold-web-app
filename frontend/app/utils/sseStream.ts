export type SSEEventStatus = "pending" | "in_progress" | "completed" | "error";

export interface SSEEvent<T = Record<string, unknown>> {
  step: string;
  status: SSEEventStatus;
  data?: T;
  error?: string;
}

export interface SSEStreamOptions<T> {
  url: string;
  method?: "GET" | "POST";
  body?: unknown;
  /** Steps with labels will show toast notifications on completion (whitelist) */
  stepLabels?: Record<string, string>;
  onEvent?: (event: SSEEvent<T>) => void;
  onStepComplete?: (step: string, data?: T) => void;
  onError?: (error: string) => void;
}

export interface SSEStreamResult<T> {
  completedSteps: Set<string>;
  lastEvent: SSEEvent<T> | null;
}

/**
 * Streams SSE events from an endpoint and handles common patterns like
 * toast notifications on step completion and error handling.
 */
export async function streamSSE<T = Record<string, unknown>>(
  options: SSEStreamOptions<T>,
): Promise<SSEStreamResult<T>> {
  const {
    url,
    method = "POST",
    body,
    stepLabels = {},
    onEvent,
    onStepComplete,
    onError,
  } = options;

  const toast = useToast();
  const completedSteps = new Set<string>();
  let lastEvent: SSEEvent<T> | null = null;

  const response = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    let errorMessage = "Request failed";
    try {
      const errorJson = JSON.parse(errorText);
      errorMessage = errorJson.detail || errorJson.message || errorMessage;
    } catch {
      if (errorText) errorMessage = errorText;
    }
    throw new Error(errorMessage);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error("No response body");
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event = JSON.parse(line.slice(6)) as SSEEvent<T>;
          lastEvent = event;

          // Skip heartbeat events
          if (event.step === "heartbeat") {
            continue;
          }

          // Notify listener of every event
          onEvent?.(event);

          // Handle error status
          if (event.status === "error") {
            const errorMsg = event.error || "Operation failed";
            onError?.(errorMsg);
            throw new Error(errorMsg);
          }

          // Handle step completion
          if (event.status === "completed" && !completedSteps.has(event.step)) {
            completedSteps.add(event.step);
            onStepComplete?.(event.step, event.data);

            // Show toast only for steps with labels (whitelist)
            const label = stepLabels[event.step];
            if (label) {
              toast.add({
                title: label,
                description: "Completed",
                color: "info",
                icon: "i-heroicons-check-circle",
                duration: 2000,
              });
            }
          }
        } catch (e) {
          // Re-throw intentional errors (from error status)
          if (e instanceof Error && e.message !== "Operation failed") {
            const isIntentionalError =
              e.message.includes("failed") ||
              e.message.includes("error") ||
              e.message.includes("Error");
            if (isIntentionalError) {
              throw e;
            }
          }
          console.error("Failed to parse SSE data:", e);
        }
      }
    }
  }

  return { completedSteps, lastEvent };
}
