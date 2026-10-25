import { nextTick } from "vue";
import {
  DRAWER_PANEL_CLASS,
  SURFACE_TRANSITION_CLASS,
} from "@/config/surfaceSelectors";

let activeTransition: ViewTransition | undefined;
let latestRequest = 0;

function waitForSurface(selector: string): Promise<HTMLElement | null> {
  const existing = document.querySelector<HTMLElement>(selector);
  if (existing) return Promise.resolve(existing);

  return new Promise((resolve) => {
    const finish = (element: HTMLElement | null) => {
      observer.disconnect();
      window.clearTimeout(timeout);
      resolve(element);
    };
    const observer = new MutationObserver(() => {
      const element = document.querySelector<HTMLElement>(selector);
      if (element) finish(element);
    });
    const timeout = window.setTimeout(() => finish(null), 1000);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
    });
  });
}

async function transitionSurface(
  source: EventTarget | null | undefined,
  update: () => unknown | Promise<unknown>,
  destination: string,
  options: { scrollToDestination?: boolean } = {},
) {
  const request = ++latestRequest;
  if (activeTransition) {
    activeTransition.skipTransition();
    await activeTransition.finished.catch(() => {});
  }
  if (request !== latestRequest) return;

  if (
    !(source instanceof HTMLElement) ||
    !source.isConnected ||
    !document.startViewTransition ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    await update();
    return;
  }

  const sourceName = source.style.viewTransitionName;
  const sourceRect = source.getBoundingClientRect();
  let restoreTarget = () => {};
  const geometryProperties = new Map<string, string>();
  const setGeometry = (name: string, value: string) => {
    geometryProperties.set(
      name,
      document.documentElement.style.getPropertyValue(name),
    );
    document.documentElement.style.setProperty(name, value);
  };
  document.documentElement.classList.add(SURFACE_TRANSITION_CLASS);
  source.style.viewTransitionName = "selected-surface";

  try {
    const transition = document.startViewTransition(async () => {
      source.style.viewTransitionName = sourceName;
      if (request !== latestRequest) return;
      await update();
      await nextTick();
      if (request !== latestRequest) return;
      const target = await waitForSurface(destination);
      if (!target || request !== latestRequest) {
        activeTransition?.skipTransition();
        return;
      }
      const targetName = target.style.viewTransitionName;
      restoreTarget = () => {
        target.style.viewTransitionName = targetName;
      };
      if (options.scrollToDestination) {
        const navBottom =
          document.querySelector("nav")?.getBoundingClientRect().bottom ?? 0;
        window.scrollTo({
          top:
            window.scrollY +
            target.getBoundingClientRect().top -
            navBottom -
            16,
          behavior: "instant",
        });
      }
      const targetRect = target.getBoundingClientRect();
      const targetHeight = target.classList.contains(DRAWER_PANEL_CLASS)
        ? targetRect.height
        : Math.min(
            targetRect.height,
            Math.max(200, window.innerHeight - Math.max(0, targetRect.top)),
          );
      const width = Math.max(sourceRect.width, targetRect.width);
      const height = Math.max(sourceRect.height, targetHeight);
      setGeometry("--surface-width", `${width}px`);
      setGeometry("--surface-height", `${height}px`);
      setGeometry("--surface-from-x", `${sourceRect.left}px`);
      setGeometry("--surface-from-y", `${sourceRect.top}px`);
      setGeometry("--surface-to-x", `${targetRect.left}px`);
      setGeometry("--surface-to-y", `${targetRect.top}px`);
      setGeometry("--surface-from-right", `${width - sourceRect.width}px`);
      setGeometry("--surface-from-bottom", `${height - sourceRect.height}px`);
      setGeometry("--surface-to-right", `${width - targetRect.width}px`);
      setGeometry("--surface-to-bottom", `${height - targetHeight}px`);
      target.dataset.surfaceEntered = "true";
      target.style.viewTransitionName = "selected-surface";
    });
    activeTransition = transition;
    void transition.ready.catch(() => {});
    await transition.finished;
  } finally {
    source.style.viewTransitionName = sourceName;
    restoreTarget();
    for (const [name, value] of geometryProperties) {
      if (value) document.documentElement.style.setProperty(name, value);
      else document.documentElement.style.removeProperty(name);
    }
    document.documentElement.classList.remove(SURFACE_TRANSITION_CLASS);
    activeTransition = undefined;
  }
}

export function useSurfaceTransition() {
  return { transitionSurface };
}
