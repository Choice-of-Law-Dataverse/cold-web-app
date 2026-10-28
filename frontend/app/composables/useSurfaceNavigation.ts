import { useRouter } from "vue-router";
import { getEntityConfig } from "@/config/entityRegistry";
import { transitionSurface } from "@/utils/surfaceTransition";
import {
  QUESTIONS_HASH,
  SURFACE_DESTINATIONS,
} from "@/config/surfaceSelectors";

function pathSegments(pathname: string): string[] {
  return pathname.split("/").filter(Boolean);
}

function destinationFor(url: URL): string {
  if (url.pathname === "/search") return SURFACE_DESTINATIONS.search;
  if (url.hash === QUESTIONS_HASH) return SURFACE_DESTINATIONS.questions;
  return pathSegments(url.pathname).length === 1
    ? SURFACE_DESTINATIONS.list
    : SURFACE_DESTINATIONS.detail;
}

export function useSurfaceNavigation() {
  const router = useRouter();

  function navigateFromElement(
    source: EventTarget | null,
    href: string,
    beforeNavigate?: () => void,
  ) {
    const url = new URL(href, window.location.href);
    const destination = destinationFor(url);

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
    const [firstSegment] = pathSegments(url.pathname);
    if (
      url.pathname !== "/search" &&
      !(firstSegment && getEntityConfig(`/${firstSegment}`))
    )
      return;
    event.preventDefault();
    return navigateFromElement(link, `${url.pathname}${url.search}${url.hash}`);
  }

  return { navigateFromElement, handleLinkClick };
}
