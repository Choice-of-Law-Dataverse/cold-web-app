import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ComparisonCaveats from "./ComparisonCaveats.vue";

describe("ComparisonCaveats", () => {
  it("renders ContentDoc with the correct path to caveats markdown", () => {
    const wrapper = mount(ComparisonCaveats, {
      global: {
        stubs: {
          ContentDoc: true,
        },
      },
    });

    // Find the stubbed ContentDoc component
    const contentDoc = wrapper.find("content-doc-stub");

    expect(contentDoc.exists()).toBe(true);
    expect(contentDoc.attributes("path")).toBe("/comparison_caveats");
  });
});
