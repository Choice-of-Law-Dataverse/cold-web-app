import { afterEach, describe, expect, it, vi } from "vitest";
import { useSurfaceTransition } from "./useSurfaceTransition";

const { transitionSurface } = useSurfaceTransition();
const originalTransition = Object.getOwnPropertyDescriptor(
  document,
  "startViewTransition",
);

function createSource() {
  const source = document.createElement("button");
  source.textContent = "Open record";
  document.body.append(source);
  return source;
}

function mockTransitions() {
  const captures: string[][] = [];
  const capture = () => {
    captures.push(
      Array.from(document.querySelectorAll<HTMLElement>("body *"))
        .filter(
          (element) => element.style.viewTransitionName === "selected-surface",
        )
        .map((element) => element.tagName),
    );
  };
  const start = vi.fn((update: () => Promise<void>) => {
    capture();
    const updated = Promise.resolve().then(update);
    const ready = updated.then(capture);
    return {
      ready,
      updateCallbackDone: updated,
      finished: ready,
      skipTransition: vi.fn(),
    } as unknown as ViewTransition;
  });
  Object.defineProperty(document, "startViewTransition", {
    configurable: true,
    value: start,
  });
  return { start, captures };
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
  if (originalTransition) {
    Object.defineProperty(document, "startViewTransition", originalTransition);
  } else {
    Reflect.deleteProperty(document, "startViewTransition");
  }
  document.body.replaceChildren();
});

describe("surface transitions", () => {
  it("matches the clicked control to a lazily mounted destination and cleans up", async () => {
    const { captures } = mockTransitions();
    const source = createSource();
    source.style.viewTransitionName = "original-control";
    const target = document.createElement("aside");
    target.id = "drawer";
    target.style.viewTransitionName = "original-panel";

    await transitionSurface(
      source,
      () => {
        window.setTimeout(() => document.body.append(target), 0);
      },
      "#drawer",
    );

    expect(captures).toEqual([["BUTTON"], ["ASIDE"]]);
    expect(source.style.viewTransitionName).toBe("original-control");
    expect(target.style.viewTransitionName).toBe("original-panel");
    expect(
      document.documentElement.classList.contains("surface-transition"),
    ).toBe(false);
  });

  it("waits for the destination to finish loading before capturing it", async () => {
    const { captures } = mockTransitions();
    const target = document.createElement("aside");
    target.id = "drawer";
    await transitionSurface(
      createSource(),
      () => {
        document.body.append(target);
        window.setTimeout(() => target.setAttribute("data-ready", ""), 0);
      },
      "#drawer[data-ready]",
    );

    expect(captures).toEqual([["BUTTON"], ["ASIDE"]]);
  });

  it("keeps navigation working without native view transitions", async () => {
    const update = vi.fn();
    await transitionSurface(createSource(), update, "#drawer");
    expect(update).toHaveBeenCalledOnce();
  });

  it("respects reduced motion", async () => {
    const { start } = mockTransitions();
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: true,
    } as MediaQueryList);
    const update = vi.fn();
    await transitionSurface(createSource(), update, "#drawer");
    expect(update).toHaveBeenCalledOnce();
    expect(start).not.toHaveBeenCalled();
  });

  it("restores the destination's scrolling and height after a viewport-sized capture", async () => {
    mockTransitions();
    const target = document.createElement("section");
    target.id = "results";
    target.style.maxHeight = "900px";
    target.style.overflow = "auto";
    await transitionSurface(
      createSource(),
      () => document.body.append(target),
      "#results",
    );
    expect(target.style.maxHeight).toBe("900px");
    expect(target.style.overflow).toBe("auto");
    expect(
      document.documentElement.style.getPropertyValue("--surface-width"),
    ).toBe("");
  });

  it("cleans up if the update fails", async () => {
    mockTransitions();
    const source = createSource();
    await expect(
      transitionSurface(
        source,
        () => {
          throw new Error("Navigation failed");
        },
        "#drawer",
      ),
    ).rejects.toThrow("Navigation failed");
    expect(source.style.viewTransitionName).toBe("");
    expect(
      document.documentElement.classList.contains("surface-transition"),
    ).toBe(false);
  });

  it("does not hold up navigation when the destination never mounts", async () => {
    vi.useFakeTimers();
    const { start } = mockTransitions();
    const update = vi.fn();
    const done = transitionSurface(createSource(), update, "#missing");
    await vi.runAllTimersAsync();
    await done;
    expect(update).toHaveBeenCalledOnce();
    expect(start.mock.results[0]?.value.skipTransition).toHaveBeenCalledOnce();
    expect(
      document.documentElement.classList.contains("surface-transition"),
    ).toBe(false);
  });

  it("honors the latest click when another transition has not updated yet", async () => {
    const { start } = mockTransitions();
    const firstUpdate = vi.fn();
    const target = document.createElement("aside");
    target.id = "drawer";
    const latestUpdate = vi.fn(() => document.body.append(target));
    const first = transitionSurface(createSource(), firstUpdate, "#drawer");
    const latest = transitionSurface(createSource(), latestUpdate, "#drawer");

    await Promise.all([first, latest]);

    expect(start.mock.results[0]?.value.skipTransition).toHaveBeenCalledOnce();
    expect(firstUpdate).not.toHaveBeenCalled();
    expect(latestUpdate).toHaveBeenCalledOnce();
    expect(target.style.viewTransitionName).toBe("");
  });
});
