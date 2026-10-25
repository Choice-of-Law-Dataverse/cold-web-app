import { useRouter } from "vue-router";
import { getEntityConfig } from "@/config/entityRegistry";
import { useSurfaceTransition } from "@/composables/useSurfaceTransition";
import { SURFACE_DESTINATIONS } from "@/config/surfaceSelectors";

export function useSurfaceNavigation() {
  const router = useRouter();
  const { transitionSurface } = useSurfaceTransition();

  function navigateFromElement(
    source: EventTarget | null,
    href: string,
    beforeNavigate?: () => void,
  ) {
    const url = new URL(href, window.location.href);
    const destination =
      url.pathname === "/search"
        ? SURFACE_DESTINATIONS.search
        : url.hash === SURFACE_DESTINATIONS.questions
          ? SURFACE_DESTINATIONS.questions
          : url.pathname.split("/").filter(Boolean).length === 1
            ? SURFACE_DESTINATIONS.list
            : SURFACE_DESTINATIONS.detail;

    return transitionSurface(
      source,
      () => {
        beforeNavigate?.();
        return router.push(href);
      },
      destination,
      { scrollToDestination: !!url.hash },
    );
  }

  function handleLinkClick(event: MouseEvent) {
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)
      return;
    const link =
      event.target instanceof Element
        ? event.target.closest<HTMLAnchorElement>("a[href]")
        : null;
    if (
      !link ||
      link.hasAttribute("download") ||
      (link.target && link.target !== "_self")
    )
      return;
    const url = new URL(link.href);
    if (url.origin !== window.location.origin) return;
    if (
      url.pathname !== "/search" &&
      !getEntityConfig(`/${url.pathname.split("/")[1]}`)
    )
      return;
    event.preventDefault();
    return navigateFromElement(link, `${url.pathname}${url.search}${url.hash}`);
  }

  return { navigateFromElement, handleLinkClick };
}
