import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import BaseLegalLink from "./BaseLegalLink.vue";

describe("BaseLegalLink", () => {
  it("renders with required 'to' prop", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
      },
      slots: {
        default: "Link text",
      },
    });
    expect(wrapper.text()).toContain("Link text");
  });

  it("uses default base class", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
      },
    });
    expect(wrapper.html()).toContain("result-value-small");
  });

  it("accepts custom base class", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        baseClass: "custom-base-class",
      },
    });
    expect(wrapper.html()).toContain("custom-base-class");
  });

  it("accepts custom class prop", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        class: "custom-additional-class",
      },
    });
    expect(wrapper.html()).toContain("custom-additional-class");
  });

  it("displays loading state with gray text", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        loading: true,
      },
    });
    expect(wrapper.text()).toContain("Loading...");
    expect(wrapper.html()).toContain("text-gray-500");
  });

  it("displays error message with red text when error prop is provided", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        error: "Something went wrong",
      },
    });
    expect(wrapper.text()).toContain("Something went wrong");
    expect(wrapper.html()).toContain("text-red-500");
  });

  it("displays slot content when not loading and no error", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
      },
      slots: {
        default: "Normal link content",
      },
    });
    expect(wrapper.text()).toContain("Normal link content");
    expect(wrapper.text()).not.toContain("Loading...");
  });

  it("prioritizes loading state over error state", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        loading: true,
        error: "Error message",
      },
    });
    expect(wrapper.text()).toContain("Loading...");
    expect(wrapper.text()).not.toContain("Error message");
  });

  it("prioritizes error state over normal content", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        error: "Error message",
      },
      slots: {
        default: "Normal content",
      },
    });
    expect(wrapper.text()).toContain("Error message");
    expect(wrapper.text()).not.toContain("Normal content");
  });

  it("applies both base class and custom class", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        baseClass: "base-class",
        class: "custom-class",
      },
    });
    expect(wrapper.html()).toContain("base-class");
    expect(wrapper.html()).toContain("custom-class");
  });

  it("handles empty class prop", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/test-path",
        class: "",
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("renders NuxtLink with correct 'to' attribute", () => {
    const wrapper = mount(BaseLegalLink, {
      props: {
        to: "/legal/document/123",
      },
    });
    // NuxtLink is stubbed in tests, check HTML instead
    expect(wrapper.html()).toContain("/legal/document/123");
  });
});
