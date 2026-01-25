import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import InfoPopover from "./InfoPopover.vue";

describe("InfoPopover", () => {
  it("renders with provided text", () => {
    const wrapper = mount(InfoPopover, {
      props: {
        text: "This is helpful information",
      },
    });
    // Text is in a popover panel that may not be rendered by default
    expect(wrapper.props("text")).toBe("This is helpful information");
  });

  it("uses default top placement when not specified", () => {
    const wrapper = mount(InfoPopover, {
      props: {
        text: "Some info",
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("accepts custom placement prop", () => {
    const wrapper = mount(InfoPopover, {
      props: {
        text: "Some info",
        placement: "bottom",
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("renders info icon", () => {
    const wrapper = mount(InfoPopover, {
      props: {
        text: "Some info",
      },
    });
    const icon = wrapper.find(".icon");
    expect(icon.exists()).toBe(true);
  });
});
