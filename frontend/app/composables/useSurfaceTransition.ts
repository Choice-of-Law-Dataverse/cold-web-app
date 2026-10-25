import { nextTick } from "vue";

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
  let restoreTarget = () => {};
  document.documentElement.classList.add("surface-transition");
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
      const maxHeight = target.style.maxHeight;
      const overflow = target.style.overflow;
      restoreTarget = () => {
        target.style.viewTransitionName = targetName;
        target.style.maxHeight = maxHeight;
        target.style.overflow = overflow;
      };
      if (target.classList.contains("entity-list-table")) {
        target.style.maxHeight = `${Math.max(200, window.innerHeight - Math.max(0, target.getBoundingClientRect().top))}px`;
        target.style.overflow = "clip";
      }
      target.dataset.surfaceEntered = "true";
      target.style.viewTransitionName = "selected-surface";
    });
    activeTransition = transition;
    void transition.ready.catch(() => {});
    await transition.finished;
  } finally {
    source.style.viewTransitionName = sourceName;
    restoreTarget();
    document.documentElement.classList.remove("surface-transition");
    activeTransition = undefined;
  }
}

export function useSurfaceTransition() {
  return { transitionSurface };
}
