import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { ref, inject, computed } from "vue";
import EntityDrawer from "./EntityDrawer.vue";
import * as entityDrawerModule from "@/composables/useEntityDrawer";
import * as entityDataModule from "@/composables/useEntityData";
import { IN_ENTITY_DRAWER_KEY } from "@/composables/useEntityDrawer";

vi.stubGlobal(
  "useRoute",
  vi.fn().mockReturnValue({
    fullPath: "/current-path",
    path: "/current-path",
    params: {},
  }),
);

describe("EntityDrawer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function mountComponent(
    drawerState: Partial<
      ReturnType<typeof entityDrawerModule.useEntityDrawer>
    > = {},
    dataState: Partial<ReturnType<typeof entityDataModule.useEntityData>> = {},
  ) {
    const mockUseEntityDrawer = {
      isOpen: ref(false),
      entity: ref(null),
      canGoBack: computed(() => false),
      closeDrawer: vi.fn(),
      goBack: vi.fn(),
      openDrawer: vi.fn(),
      ...drawerState,
    };
    vi.spyOn(entityDrawerModule, "useEntityDrawer").mockReturnValue(
      mockUseEntityDrawer as unknown as ReturnType<
        typeof entityDrawerModule.useEntityDrawer
      >,
    );

    const mockUseEntityData = {
      data: ref(null),
      isLoading: ref(false),
      error: ref(null),
      config: ref({}),
      ...dataState,
    };
    vi.spyOn(entityDataModule, "useEntityData").mockReturnValue(
      mockUseEntityData as unknown as ReturnType<
        typeof entityDataModule.useEntityData
      >,
    );

    return mount(EntityDrawer, {
      global: {
        stubs: {
          USlideover: {
            template:
              '<div class="u-slideover" v-if="open"><slot name="content" /></div>',
            props: ["open"],
          },
          UButton: true,
          MetaBand: true,
          GradientTopBorder: true,
          LoadingBar: true,
          InlineError: true,
          EntityContent: true,
          CourtDecisionContent: true,
          JurisdictionDrawerQA: true,
          DrawerAnswerMap: true,
        },
      },
    });
  }

  it("renders when open", () => {
    const wrapper = mountComponent({
      isOpen: ref(true),
    });
    expect(wrapper.find(".u-slideover").exists()).toBe(true);
  });

  it("calls goBack when back button is clicked", async () => {
    const mockGoBack = vi.fn();
    const wrapper = mountComponent({
      isOpen: ref(true),
      canGoBack: computed(() => true),
      goBack: mockGoBack,
    });

    const backBtn = wrapper.findComponent('[icon="i-lucide-arrow-left"]');
    expect(backBtn.exists()).toBe(true);
    await backBtn.trigger("click");

    expect(mockGoBack).toHaveBeenCalled();
  });

  it("calls closeDrawer when close button is clicked", async () => {
    const mockCloseDrawer = vi.fn();
    const wrapper = mountComponent({
      isOpen: ref(true),
      closeDrawer: mockCloseDrawer,
    });

    const closeBtn = wrapper.findComponent('[icon="i-lucide-x"]');
    expect(closeBtn.exists()).toBe(true);
    await closeBtn.trigger("click");

    expect(mockCloseDrawer).toHaveBeenCalled();
  });

  it("shows loading bar when isLoading is true", () => {
    const wrapper = mountComponent(
      { isOpen: ref(true) },
      { isLoading: ref(true) },
    );
    expect(wrapper.findComponent({ name: "LoadingBar" }).exists()).toBe(true);
  });

  it("shows InlineError when error is present", () => {
    const wrapper = mountComponent(
      { isOpen: ref(true) },
      { error: ref(new Error("Test error")) },
    );
    expect(wrapper.findComponent({ name: "InlineError" }).exists()).toBe(true);
  });

  it("provides in-entity-drawer context to its children", () => {
    let providedValue: unknown;

    const mockUseEntityDrawer = {
      isOpen: ref(true),
      entity: ref(null),
      canGoBack: computed(() => false),
      closeDrawer: vi.fn(),
      openDrawer: vi.fn(),
      goBack: vi.fn(),
    };
    vi.spyOn(entityDrawerModule, "useEntityDrawer").mockReturnValue(
      mockUseEntityDrawer as unknown as ReturnType<
        typeof entityDrawerModule.useEntityDrawer
      >,
    );
    vi.spyOn(entityDataModule, "useEntityData").mockReturnValue({
      data: ref(null),
      isLoading: ref(false),
      error: ref(null),
      config: ref({}),
    } as unknown as ReturnType<typeof entityDataModule.useEntityData>);

    mount(EntityDrawer, {
      global: {
        stubs: {
          USlideover: {
            setup() {
              providedValue = inject(IN_ENTITY_DRAWER_KEY);
              return () => null;
            },
          },
        },
      },
    });

    expect(providedValue).toBe(true);
  });
});
