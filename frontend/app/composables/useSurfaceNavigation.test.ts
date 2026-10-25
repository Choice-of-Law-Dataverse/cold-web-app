import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useSurfaceNavigation } from "./useSurfaceNavigation";

const { push, transitionSurface } = vi.hoisted(() => ({
  push: vi.fn(),
  transitionSurface: vi.fn(
    (_source: unknown, update: () => unknown, _destination: string) => update(),
  ),
}));

vi.mock("vue-router", () => ({ useRouter: () => ({ push }) }));
vi.mock("./useSurfaceTransition", () => ({
  useSurfaceTransition: () => ({ transitionSurface }),
}));

beforeEach(() => vi.clearAllMocks());
afterEach(() => document.body.replaceChildren());

function clickLink(
  href: string,
  options: MouseEventInit = {},
  attributes: Record<string, string> = {},
) {
  const root = document.createElement("div");
  const link = document.createElement("a");
  link.href = href;
  for (const [name, value] of Object.entries(attributes))
    link.setAttribute(name, value);
  const title = document.createElement("span");
  title.textContent = "Open research";
  link.append(title);
  root.append(link);
  document.body.append(root);
  const { handleLinkClick } = useSurfaceNavigation();
  root.addEventListener("click", handleLinkClick, { capture: true });
  const event = new MouseEvent("click", {
    bubbles: true,
    cancelable: true,
    ...options,
  });
  title.dispatchEvent(event);
  return { event, link };
}

describe("homepage surface navigation", () => {
  it.each([
    ["/court-decision", '.entity-list-table:not([aria-busy="true"])'],
    [
      "/court-decision?caseRank=10",
      '.entity-list-table:not([aria-busy="true"])',
    ],
    [
      "/search?type=Domestic+Instruments&sortBy=date",
      "[data-search-surface][data-surface-ready]",
    ],
    ["/court-decision/CD-DEU-362", "[data-detail-surface][data-surface-ready]"],
    [
      "/international-instrument/II-Pri-1",
      "[data-detail-surface][data-surface-ready]",
    ],
    [
      "/jurisdiction/CHE?compare=CAN#questions-and-answers",
      "#questions-and-answers",
    ],
  ])("connects %s to its destination", (href, destination) => {
    const { event, link } = clickLink(href);
    expect(event.defaultPrevented).toBe(true);
    expect(transitionSurface).toHaveBeenCalledWith(
      link,
      expect.any(Function),
      destination,
      { scrollToDestination: href.includes("#") },
    );
    expect(push).toHaveBeenCalledWith(href);
  });

  it.each(["metaKey", "ctrlKey", "shiftKey", "altKey"])(
    "preserves %s clicks",
    (key) => {
      const { event } = clickLink("/court-decision", { [key]: true });
      expect(event.defaultPrevented).toBe(false);
      expect(transitionSurface).not.toHaveBeenCalled();
    },
  );

  it.each([
    ["https://example.com", {}],
    ["/about", {}],
    ["/court-decision", { target: "_blank" }],
    ["/court-decision", { download: "data" }],
  ])("leaves ordinary navigation intact for %s %o", (href, attributes) => {
    const { event } = clickLink(href, {}, attributes);
    expect(event.defaultPrevented).toBe(false);
    expect(push).not.toHaveBeenCalled();
  });

  it("runs button preparation inside the transition before navigating", async () => {
    const { navigateFromElement } = useSurfaceNavigation();
    const prepare = vi.fn(() => expect(push).not.toHaveBeenCalled());
    await navigateFromElement(
      document.createElement("button"),
      "/search?q=party",
      prepare,
    );
    expect(prepare).toHaveBeenCalledOnce();
    expect(push).toHaveBeenCalledWith("/search?q=party");
  });
});
