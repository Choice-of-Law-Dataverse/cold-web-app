import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import ComparisonHeader from "./ComparisonHeader.vue";
import { ComparisonStateKey } from "./comparisonState";
import { computed } from "vue";

// Mock UI components
const UIconStub = { template: '<span class="u-icon-mock"></span>' };

describe("ComparisonHeader", () => {
  const defaultState = {
    jurisdictions: computed(() => [
      { coldId: "US", name: "United States" },
      { coldId: "UK", name: "United Kingdom" }
    ]),
    removeJurisdiction: vi.fn(),
    isScrollable: computed(() => false),
    stickyColLeft: computed(() => "0px"),
    jurisdictionLabel: (j: any) => j.name,
  };

  const createWrapper = (stateOverride = {}) => {
    return mount(ComparisonHeader, {
      global: {
        components: {
          UIcon: UIconStub,
        },
        provide: {
          [ComparisonStateKey as symbol]: {
            ...defaultState,
            ...stateOverride,
          },
        },
      },
    });
  };

  it("renders headers for each jurisdiction", () => {
    const wrapper = createWrapper();
    const cells = wrapper.findAll(".comparison-header-cell.text-center");
    expect(cells).toHaveLength(2);
    expect(cells[0].text()).toContain("United States");
    expect(cells[1].text()).toContain("United Kingdom");
  });

  it("disables the remove button for the primary (first) jurisdiction", () => {
    const wrapper = createWrapper();
    const buttons = wrapper.findAll(".jurisdiction-action-button");
    expect(buttons[0].attributes("disabled")).toBeDefined();
    expect(buttons[1].attributes("disabled")).toBeUndefined();
  });

  it("calls removeJurisdiction when clicking the remove button on secondary jurisdictions", async () => {
    const removeJurisdiction = vi.fn();
    const wrapper = createWrapper({ removeJurisdiction });
    
    const buttons = wrapper.findAll(".jurisdiction-action-button");
    await buttons[1].trigger("click");
    
    expect(removeJurisdiction).toHaveBeenCalledWith("UK");
  });

  it("applies sticky classes when scrollable", () => {
    const wrapper = createWrapper({
      isScrollable: computed(() => true),
      stickyColLeft: computed(() => "200px")
    });
    
    const cells = wrapper.findAll(".comparison-header-cell.text-center");
    expect(cells[0].classes()).toContain("sticky-col-2");
    expect(cells[1].classes()).not.toContain("sticky-col-2");
    
    // Check match column
    const matchCol = wrapper.find(".comparison-header-cell--match");
    expect(matchCol.classes()).toContain("sticky-col-match");
  });
});
