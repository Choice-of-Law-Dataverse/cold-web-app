import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import CompatibleLabel from "./CompatibleLabel.vue";

describe("CompatibleLabel", () => {
  it("renders with default label", () => {
    const wrapper = mount(CompatibleLabel);
    expect(wrapper.text()).toContain("Your fav Law");
  });

  it("renders with custom label prop", () => {
    const wrapper = mount(CompatibleLabel, {
      props: {
        label: "Custom Law",
      },
    });
    expect(wrapper.text()).toContain("Custom Law");
  });

  it("renders the icon", () => {
    const wrapper = mount(CompatibleLabel);
    expect(wrapper.find(".icon-fixed").exists()).toBe(true);
  });

  it("applies correct CSS classes", () => {
    const wrapper = mount(CompatibleLabel);
    expect(wrapper.find(".label-question").exists()).toBe(true);
    expect(wrapper.classes()).toContain("label-question");
  });
});
