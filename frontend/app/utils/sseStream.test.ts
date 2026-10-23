import { describe, it, expect, vi, afterEach } from "vitest";
import { streamSSE, type SSEEvent } from "./sseStream";

function respondWith(...chunks: string[]) {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response(body, { status: 200 })),
  );
}

const line = (event: SSEEvent) => `data: ${JSON.stringify(event)}\n`;

describe("streamSSE", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("delivers events split across chunks and skips heartbeats", async () => {
    const full = line({ step: "a", status: "completed", data: { x: 1 } });
    respondWith(
      full.slice(0, 10),
      full.slice(10),
      line({ step: "heartbeat", status: "in_progress" }),
    );
    const onEvent = vi.fn();
    const onStepComplete = vi.fn();

    const result = await streamSSE({ url: "/x", onEvent, onStepComplete });

    expect(onEvent).toHaveBeenCalledTimes(1);
    expect(onStepComplete).toHaveBeenCalledWith("a", { x: 1 });
    expect([...result.completedSteps]).toEqual(["a"]);
  });

  it("skips malformed lines", async () => {
    respondWith("data: {not json\n", line({ step: "a", status: "completed" }));
    const onEvent = vi.fn();

    await streamSSE({ url: "/x", onEvent });

    expect(onEvent).toHaveBeenCalledTimes(1);
  });

  it("rejects on an error event", async () => {
    respondWith(line({ step: "a", status: "error", error: "Boom" }));
    const onError = vi.fn();

    await expect(streamSSE({ url: "/x", onError })).rejects.toThrow("Boom");
    expect(onError).toHaveBeenCalledWith("Boom");
  });

  it("rejects when a handler throws", async () => {
    respondWith(line({ step: "a", status: "completed" }));

    await expect(
      streamSSE({
        url: "/x",
        onEvent: () => {
          throw new Error("handler failed");
        },
      }),
    ).rejects.toThrow("handler failed");
  });

  it("rejects when the request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("", { status: 500 })),
    );

    await expect(streamSSE({ url: "/x" })).rejects.toThrow("Request failed");
  });
});
