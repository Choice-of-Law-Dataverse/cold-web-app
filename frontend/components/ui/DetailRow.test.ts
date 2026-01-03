import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DetailRow from "./DetailRow.vue";

describe("DetailRow", () => {
  it("renders label text", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Field Label",
      },
    });
    expect(wrapper.text()).toContain("Field Label");
  });

  it("renders slot content", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Label",
      },
      slots: {
        default: "This is the content",
      },
    });
    expect(wrapper.text()).toContain("This is the content");
  });

  it("does not render InfoPopover when no tooltip provided", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Label",
      },
    });
    expect(wrapper.findComponent({ name: "InfoPopover" }).exists()).toBe(false);
  });

  it("renders InfoPopover when tooltip is provided", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Label",
        tooltip: "This is a helpful tip",
      },
    });
    expect(wrapper.findComponent({ name: "InfoPopover" }).exists()).toBe(true);
  });

  it("renders label-actions slot content", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Label",
      },
      slots: {
        "label-actions": "<button>Action</button>",
      },
    });
    expect(wrapper.html()).toContain("<button>Action</button>");
  });

  it("has correct flex layout structure", () => {
    const wrapper = mount(DetailRow, {
      props: {
        label: "Label",
      },
    });
    const container = wrapper.find("div");
    expect(container.classes()).toContain("flex");
    expect(container.classes()).toContain("flex-col");
  });
});
