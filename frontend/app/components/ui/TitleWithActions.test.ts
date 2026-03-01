import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import TitleWithActions from "./TitleWithActions.vue";

describe("TitleWithActions", () => {
  it("renders default slot content", () => {
    const wrapper = mount(TitleWithActions, {
      slots: {
        default: "Case Title Text",
      },
    });
    expect(wrapper.text()).toContain("Case Title Text");
  });

  it("renders actions slot content", () => {
    const wrapper = mount(TitleWithActions, {
      slots: {
        default: "Title",
        actions: "<button>Download PDF</button>",
      },
    });
    expect(wrapper.html()).toContain("<button>Download PDF</button>");
  });

  it("applies default titleClass", () => {
    const wrapper = mount(TitleWithActions, {
      slots: { default: "Title" },
    });
    expect(wrapper.html()).toContain("result-value-small");
    expect(wrapper.html()).toContain("flex-1");
  });

  it("applies custom titleClass prop", () => {
    const wrapper = mount(TitleWithActions, {
      props: { titleClass: "custom-class" },
      slots: { default: "Title" },
    });
    expect(wrapper.html()).toContain("custom-class");
    expect(wrapper.html()).not.toContain("result-value-small");
  });

  it("has correct flex layout structure", () => {
    const wrapper = mount(TitleWithActions, {
      slots: { default: "Title" },
    });
    const root = wrapper.element;
    expect(root.classList.contains("flex")).toBe(true);
    expect(root.classList.contains("items-start")).toBe(true);
    expect(root.classList.contains("justify-between")).toBe(true);
    expect(root.classList.contains("gap-4")).toBe(true);
  });

  it("actions container has correct layout classes", () => {
    const wrapper = mount(TitleWithActions, {
      slots: { default: "Title", actions: "<span>Action</span>" },
    });
    const actionsDiv = wrapper.element.children[1] as HTMLElement;
    expect(actionsDiv.classList.contains("flex-shrink-0")).toBe(true);
    expect(actionsDiv.classList.contains("flex")).toBe(true);
  });
});
