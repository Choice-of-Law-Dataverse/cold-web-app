import { ref } from "vue";

export type NavigationDirection = "forward" | "back" | "none";

// Global state shared across all uses
const direction = ref<NavigationDirection>("none");
const currentPosition = ref(0);

/**
 * Composable for detecting navigation direction (forward vs back).
 * This enables direction-aware page transitions for better UX,
 * especially for browser back/forward button usage.
 */
export function useNavigationDirection() {
  return {
    direction,
    currentPosition,
  };
}

/**
 * Plugin to initialize navigation direction tracking.
 * Should be called once in a Nuxt plugin.
 *
 * Uses history.state to reliably track position and detect back/forward navigation.
 */
export function initNavigationDirection() {
  if (!import.meta.client) return;

  const router = useRouter();

  // Initialize position from history.state or start at 0
  const getHistoryPosition = (): number => {
    return (history.state?.position as number) ?? 0;
  };

  // Set initial position
  currentPosition.value = getHistoryPosition();

  // Ensure current history entry has a position
  if (history.state?.position === undefined) {
    const newState = { ...history.state, position: currentPosition.value };
    history.replaceState(newState, "");
  }

  router.beforeEach((to, from) => {
    if (!from.name) {
      // Initial navigation - no transition direction
      direction.value = "none";
      return;
    }

    const previousPosition = currentPosition.value;
    const newPosition = getHistoryPosition();

    if (newPosition < previousPosition) {
      // Going back in history
      direction.value = "back";
    } else if (newPosition > previousPosition) {
      // Going forward (could be new navigation or browser forward)
      direction.value = "forward";
    } else {
      // Same position (e.g., replace navigation) - use forward as default
      direction.value = "forward";
    }

    currentPosition.value = newPosition;
  });

  router.afterEach((to, from, failure) => {
    if (failure) return;

    // For new navigations (not back/forward), increment position
    // Vue Router automatically handles history.state for push navigations
    const newPosition = getHistoryPosition();

    // If this was a push navigation, ensure position is set
    if (history.state?.position === undefined) {
      const nextPosition = currentPosition.value + 1;
      const newState = { ...history.state, position: nextPosition };
      history.replaceState(newState, "");
      currentPosition.value = nextPosition;
    } else {
      currentPosition.value = newPosition;
    }
  });
}
