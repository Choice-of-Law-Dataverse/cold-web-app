class SSEApplicationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SSEApplicationError";
  }
}

export type SSEEventStatus = "pending" | "in_progress" | "completed" | "error";

export interface SSEEvent<T = Record<string, unknown>> {
  step: string;
  status: SSEEventStatus;
  data?: T;
  error?: string;
}

export interface ToastHandle {
  add: (opts: {
    title: string;
    description: string;
    color: string;
    icon: string;
    duration: number;
  }) => void;
}

export interface SSEStreamOptions<T> {
  url: string;
  method?: "GET" | "POST";
  body?: unknown;
  toast?: ToastHandle;
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
    toast,
    stepLabels = {},
    onEvent,
    onStepComplete,
    onError,
  } = options;
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
    throw new Error("Request failed");
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error("No response body");
  }

  let buffer = "";

  function processEvent(event: SSEEvent<T>) {
    lastEvent = event;

    if (event.step === "heartbeat") return;

    onEvent?.(event);

    if (event.status === "error") {
      const errorMsg = event.error || "Operation failed";
      onError?.(errorMsg);
      throw new SSEApplicationError(errorMsg);
    }

    if (event.status === "completed" && !completedSteps.has(event.step)) {
      completedSteps.add(event.step);
      onStepComplete?.(event.step, event.data);

      const label = stepLabels[event.step];
      if (label && toast) {
        toast.add({
          title: label,
          description: "Completed",
          color: "info",
          icon: "i-heroicons-check-circle",
          duration: 2000,
        });
      }
    }
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n");
    buffer = parts.pop() ?? "";

    for (const line of parts) {
      if (line.startsWith("data: ")) {
        try {
          const event = JSON.parse(line.slice(6)) as SSEEvent<T>;
          processEvent(event);
        } catch (e) {
          if (e instanceof SSEApplicationError) throw e;
        }
      }
    }
  }

  return { completedSteps, lastEvent };
}
