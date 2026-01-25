import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ShowMoreLess from "./ShowMoreLess.vue";

describe("ShowMoreLess", () => {
  it("renders 'Show more' when collapsed", () => {
    const wrapper = mount(ShowMoreLess, {
      props: {
        isExpanded: false,
        label: "items",
      },
    });
    expect(wrapper.text()).toContain("Show more items");
  });

  it("renders 'Show less' when expanded", () => {
    const wrapper = mount(ShowMoreLess, {
      props: {
        isExpanded: true,
        label: "items",
      },
    });
    expect(wrapper.text()).toContain("Show less items");
  });

  it("emits update:isExpanded with true when clicking show more", async () => {
    const wrapper = mount(ShowMoreLess, {
      props: {
        isExpanded: false,
        label: "items",
      },
    });
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted("update:isExpanded")).toBeTruthy();
    expect(wrapper.emitted("update:isExpanded")?.[0]).toEqual([true]);
  });

  it("emits update:isExpanded with false when clicking show less", async () => {
    const wrapper = mount(ShowMoreLess, {
      props: {
        isExpanded: true,
        label: "items",
      },
    });
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted("update:isExpanded")).toBeTruthy();
    expect(wrapper.emitted("update:isExpanded")?.[0]).toEqual([false]);
  });

  it("renders with empty label by default", () => {
    const wrapper = mount(ShowMoreLess, {
      props: {
        isExpanded: false,
      },
    });
    expect(wrapper.text()).toContain("Show more");
  });
});
