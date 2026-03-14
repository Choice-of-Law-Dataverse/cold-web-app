import { ref } from "vue";

export type NavigationDirection = "forward" | "back" | "none";

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

  const getHistoryPosition = (): number => {
    return (history.state?.position as number) ?? 0;
  };

  currentPosition.value = getHistoryPosition();

  if (history.state?.position === undefined) {
    const newState = { ...history.state, position: currentPosition.value };
    history.replaceState(newState, "");
  }

  router.beforeEach((_to, from) => {
    if (!from.name) {
      direction.value = "none";
      return;
    }

    const previousPosition = currentPosition.value;
    const newPosition = getHistoryPosition();

    direction.value = newPosition < previousPosition ? "back" : "forward";

    currentPosition.value = newPosition;
  });

  router.afterEach((_to, _from, failure) => {
    if (failure) return;

    const newPosition = getHistoryPosition();

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
