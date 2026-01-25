import { ref } from "vue";

export type NavigationDirection = "forward" | "back" | "none";

// Global state shared across all uses
const direction = ref<NavigationDirection>("none");
const historyStack = ref<string[]>([]);
const isPopState = ref(false);

/**
 * Composable for detecting navigation direction (forward vs back).
 * This enables direction-aware page transitions for better UX,
 * especially for browser back/forward button usage.
 */
export function useNavigationDirection() {
  return {
    direction,
    historyStack,
    isPopState,
  };
}

/**
 * Plugin to initialize navigation direction tracking.
 * Should be called once in a Nuxt plugin.
 */
export function initNavigationDirection() {
  const router = useRouter();

  // Track popstate (browser back/forward)
  if (import.meta.client) {
    window.addEventListener("popstate", () => {
      isPopState.value = true;
    });
  }

  // Use router beforeEach to determine direction
  router.beforeEach((to, from) => {
    if (!from.name) {
      // Initial navigation
      direction.value = "none";
      historyStack.value = [to.fullPath];
      return;
    }

    if (isPopState.value) {
      // Browser back/forward was used
      const currentIndex = historyStack.value.indexOf(from.fullPath);
      const targetIndex = historyStack.value.indexOf(to.fullPath);

      if (targetIndex !== -1 && targetIndex < currentIndex) {
        // Going back in history
        direction.value = "back";
        // Remove entries after the target
        historyStack.value = historyStack.value.slice(0, targetIndex + 1);
      } else if (targetIndex !== -1 && targetIndex > currentIndex) {
        // Going forward in history (rare, but possible with forward button)
        direction.value = "forward";
      } else {
        // Unknown position, treat as back
        direction.value = "back";
      }
    } else {
      // Normal navigation (link click, programmatic)
      direction.value = "forward";
      historyStack.value.push(to.fullPath);

      // Limit stack size to prevent memory issues
      if (historyStack.value.length > 50) {
        historyStack.value = historyStack.value.slice(-50);
      }
    }
  });

  router.afterEach(() => {
    // Reset popstate flag after navigation completes
    isPopState.value = false;
  });
}
