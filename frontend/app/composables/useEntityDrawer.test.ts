import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { defineComponent } from "vue";
import { mount } from "@vue/test-utils";
import { useEntityDrawer } from "./useEntityDrawer";

// Mock navigateTo which is a Nuxt auto-import
const mockNavigateTo = vi.fn();
vi.stubGlobal("navigateTo", mockNavigateTo);

describe("useEntityDrawer", () => {
  let originalInnerWidth: number;

  beforeEach(() => {
    vi.clearAllMocks();
    originalInnerWidth = window.innerWidth;

    // Clear state properly inside a setup to avoid warnings
    const TestComponent = defineComponent({
      setup() {
        const { closeDrawer } = useEntityDrawer();
        closeDrawer();
        return {};
      },
      template: "<div></div>",
    });
    mount(TestComponent);
  });

  afterEach(() => {
    window.innerWidth = originalInnerWidth;
  });

  function setupDrawer(inDrawer = false) {
    let result: ReturnType<typeof useEntityDrawer> | undefined;
    const TestComponent = defineComponent({
      setup() {
        result = useEntityDrawer();
        return {};
      },
      template: "<div></div>",
    });

    mount(TestComponent, {
      global: {
        provide: {
          "in-entity-drawer": inDrawer,
        },
      },
    });

    return result!;
  }

  it("opens drawer and sets entity", () => {
    window.innerWidth = 1024;
    const { isOpen, entity, openDrawer } = setupDrawer(false);
    expect(isOpen.value).toBe(false);

    openDrawer("123", "Court Decisions", "/court-decision");

    expect(isOpen.value).toBe(true);
    expect(entity.value).toEqual({
      coldId: "123",
      table: "Court Decisions",
      basePath: "/court-decision",
    });
  });

  it("navigates instead of opening drawer on mobile if forceDrawer is false", () => {
    window.innerWidth = 500; // less than 640
    const { isOpen, openDrawer } = setupDrawer(false);

    openDrawer("123", "Court Decisions", "/court-decision");

    expect(isOpen.value).toBe(false);
    expect(mockNavigateTo).toHaveBeenCalledWith("/court-decision/123");
  });

  it("opens drawer on mobile if forceDrawer is true", () => {
    window.innerWidth = 500;
    const { isOpen, openDrawer } = setupDrawer(false);

    openDrawer("123", "Court Decisions", "/court-decision", true);

    expect(isOpen.value).toBe(true);
    expect(mockNavigateTo).not.toHaveBeenCalled();
  });

  it("resets history when opening from outside the drawer context", () => {
    window.innerWidth = 1024;
    const { openDrawer, canGoBack } = setupDrawer(false);

    openDrawer("123", "Court Decisions", "/court-decision");
    openDrawer("456", "Court Decisions", "/court-decision");

    expect(canGoBack.value).toBe(false);
  });

  it("does not reset history and allows goBack when opened from inside the drawer", () => {
    window.innerWidth = 1024;

    const drawer = setupDrawer(true);

    drawer.openDrawer("123", "Court Decisions", "/court-decision");
    // Open a second entity while context is inside drawer
    drawer.openDrawer("456", "Court Decisions", "/court-decision");

    expect(drawer.canGoBack.value).toBe(true);
    expect(drawer.entity.value?.coldId).toBe("456");

    drawer.goBack();
    expect(drawer.entity.value?.coldId).toBe("123");
    expect(drawer.canGoBack.value).toBe(false);
  });

  it("short-circuits if trying to open the exact same entity", () => {
    window.innerWidth = 1024;

    const drawer = setupDrawer(true);

    drawer.openDrawer("123", "Court Decisions", "/court-decision");
    expect(drawer.canGoBack.value).toBe(false);

    // Try to open the exact same entity again
    drawer.openDrawer("123", "Court Decisions", "/court-decision");

    // History should not have been updated
    expect(drawer.canGoBack.value).toBe(false);
  });

  it("closes the drawer and resets state", () => {
    window.innerWidth = 1024;
    const { isOpen, entity, openDrawer, closeDrawer, canGoBack } =
      setupDrawer(false);

    openDrawer("123", "Court Decisions", "/court-decision");
    expect(isOpen.value).toBe(true);

    closeDrawer();
    expect(isOpen.value).toBe(false);
    expect(entity.value).toBeNull();
    expect(canGoBack.value).toBe(false);
  });
});
