import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { ref, inject, computed, toValue } from "vue";
import EntityDrawer from "./EntityDrawer.vue";
import * as entityDrawerModule from "@/composables/useEntityDrawer";
import * as entityDataModule from "@/composables/useEntityData";
import { IN_ENTITY_DRAWER_KEY } from "@/composables/useEntityDrawer";
import { getEntityConfig, type ProcessedEntity } from "@/config/entityRegistry";

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
            name: "USlideover",
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

  it("keeps the current preview and its links until the next record is ready", async () => {
    const entity = ref({
      coldId: "CD-1",
      table: "Court Decisions" as const,
      basePath: "/court-decision",
    });
    const data = ref<ProcessedEntity | null>({
      coldId: "CD-1",
      caseTitle: "First",
    } as ProcessedEntity);
    const pending = ref(false);
    const wrapper = mountComponent(
      { isOpen: ref(true), entity },
      {
        data: computed(() => data.value),
        config: computed(() => getEntityConfig("/court-decision")),
        isLoading: pending,
      },
    );
    const firstContent = wrapper.findComponent({
      name: "CourtDecisionContent",
    }).element;

    pending.value = true;
    data.value = null;
    entity.value = { ...entity.value, coldId: "CD-2" };
    await wrapper.vm.$nextTick();

    expect(
      wrapper.findComponent({ name: "CourtDecisionContent" }).element,
    ).toBe(firstContent);
    expect(
      wrapper.findComponent({ name: "MetaBand" }).props("resultData"),
    ).toMatchObject({ coldId: "CD-1" });
    expect(
      wrapper
        .findComponent('[leading-icon="i-lucide-maximize"]')
        .attributes("to"),
    ).toBe("/court-decision/CD-1");
    expect(wrapper.findComponent({ name: "LoadingBar" }).exists()).toBe(false);
    expect(wrapper.find('[role="status"]').text()).toBe("Loading preview…");

    data.value = { coldId: "CD-2", caseTitle: "Second" } as ProcessedEntity;
    pending.value = false;
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(
      wrapper.findComponent({ name: "CourtDecisionContent" }).props("data"),
    ).toMatchObject({ coldId: "CD-2" });
    expect(
      wrapper.findComponent({ name: "MetaBand" }).props("resultData"),
    ).toMatchObject({ coldId: "CD-2" });
    expect(
      wrapper
        .findComponent('[leading-icon="i-lucide-maximize"]')
        .attributes("to"),
    ).toBe("/court-decision/CD-2");
    expect(wrapper.find('[role="status"]').exists()).toBe(false);
  });

  it("keeps the entity during exit and clears it after the drawer leaves", async () => {
    const isOpen = ref(true);
    const entity = ref({
      coldId: "CD-1",
      table: "Court Decisions" as const,
      basePath: "/court-decision",
    } as ReturnType<
      typeof entityDrawerModule.useEntityDrawer
    >["entity"]["value"]);
    const wrapper = mountComponent({ isOpen, entity });
    const slideover = wrapper.findComponent({ name: "USlideover" });
    const [basePath, coldId] = vi
      .mocked(entityDataModule.useEntityData)
      .mock.calls.at(-1)!;

    isOpen.value = false;
    entity.value = null;
    await wrapper.vm.$nextTick();

    expect(toValue(basePath)).toBe("/court-decision");
    expect(toValue(coldId)).toBe("CD-1");

    slideover.vm.$emit("after:leave");
    await wrapper.vm.$nextTick();

    expect(toValue(coldId)).toBe("");
  });

  it("does not clear a reopened drawer when an earlier exit finishes", async () => {
    const isOpen = ref(true);
    const entity = ref({
      coldId: "CD-1",
      table: "Court Decisions" as const,
      basePath: "/court-decision",
    } as ReturnType<
      typeof entityDrawerModule.useEntityDrawer
    >["entity"]["value"]);
    const wrapper = mountComponent({ isOpen, entity });
    const [, coldId] = vi
      .mocked(entityDataModule.useEntityData)
      .mock.calls.at(-1)!;

    isOpen.value = false;
    entity.value = null;
    await wrapper.vm.$nextTick();
    entity.value = {
      coldId: "CD-2",
      table: "Court Decisions",
      basePath: "/court-decision",
    };
    isOpen.value = true;
    await wrapper.vm.$nextTick();
    wrapper.findComponent({ name: "USlideover" }).vm.$emit("after:leave");
    await wrapper.vm.$nextTick();

    expect(toValue(coldId)).toBe("CD-2");
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
