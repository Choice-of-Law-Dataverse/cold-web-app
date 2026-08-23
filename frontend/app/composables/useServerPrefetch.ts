import { onServerPrefetch } from "vue";

/**
 * Resolves a vue-query `suspense()` promise during server-side rendering.
 *
 * `@tanstack/vue-query` v5 does not prefetch on the server by itself. Without
 * an explicit `await suspense()` the query client is still empty when Nuxt
 * dehydrates it, so the rendered HTML ships loading placeholders instead of
 * content and every page looks identical to a crawler.
 *
 * A rejected prefetch is swallowed by default so a flaky upstream degrades to
 * a client-side retry rather than a 500. Pass `onError` to turn a specific
 * failure into an HTTP status — anything it throws propagates to Nuxt.
 *
 * @param suspense The `suspense` function returned by `useQuery`.
 * @param onError Called with the rejection reason; may throw to fail the render.
 */
export function useServerPrefetch(
  suspense: () => Promise<unknown>,
  onError?: (error: unknown) => void,
): void {
  if (!import.meta.server) return;

  onServerPrefetch(async () => {
    try {
      await suspense();
    } catch (error) {
      onError?.(error);
    }
  });
}
