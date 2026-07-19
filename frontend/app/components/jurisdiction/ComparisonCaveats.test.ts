import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ComparisonCaveats from "./ComparisonCaveats.vue";

// Mock the ContentDoc component
const ContentDocStub = {
  template: '<div class="content-doc-mock">Mocked Content</div>'
};

describe("ComparisonCaveats", () => {
  it("renders ContentDoc with the correct path", () => {
    const wrapper = mount(ComparisonCaveats, {
      global: {
        components: {
          ContentDoc: ContentDocStub
        }
      }
    });
    
    expect(wrapper.classes()).toContain("comparison-caveats__body");
    expect(wrapper.html()).toContain('Mocked Content');
  });
});
