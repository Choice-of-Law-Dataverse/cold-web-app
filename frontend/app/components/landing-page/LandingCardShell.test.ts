import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import LandingCardShell from "./LandingCardShell.vue";

const stubs = {
  UCard: defineComponent({
    setup(_, { slots }) {
      return () => h("div", { class: "u-card-stub" }, slots.default?.());
    },
  }),
  NuxtLink: defineComponent({
    props: ["to"],
    setup(props, { slots }) {
      return () =>
        h("a", { href: props.to, class: "nuxt-link" }, slots.default?.());
    },
  }),
  LoadingLandingPageCard: defineComponent({
    setup() {
      return () => h("div", { class: "loading-stub" }, "Loading...");
    },
  }),
  InlineError: defineComponent({
    props: ["error"],
    setup(props) {
      return () => h("div", { class: "error-stub" }, props.error?.message);
    },
  }),
};

const defaultProps = {
  title: "Leading Cases",
  subtitle: "Read top-ranked court decisions",
};

describe("LandingCardShell", () => {
  it("renders title and subtitle", () => {
    const wrapper = mount(LandingCardShell, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.text()).toContain("Leading Cases");
    expect(wrapper.text()).toContain("Read top-ranked court decisions");
  });

  it("renders default slot content when not loading", () => {
    const wrapper = mount(LandingCardShell, {
      props: defaultProps,
      slots: { default: "<span>Item 1</span>" },
      global: { stubs },
    });
    expect(wrapper.html()).toContain("Item 1");
  });

  it("shows loading state when loading is true", () => {
    const wrapper = mount(LandingCardShell, {
      props: { ...defaultProps, loading: true },
      slots: { default: "<span>Hidden</span>" },
      global: { stubs },
    });
    expect(wrapper.find(".loading-stub").exists()).toBe(true);
    expect(wrapper.html()).not.toContain("Hidden");
  });

  it("shows error state when error is provided", () => {
    const wrapper = mount(LandingCardShell, {
      props: { ...defaultProps, error: new Error("Something went wrong") },
      slots: { default: "<span>Hidden</span>" },
      global: { stubs },
    });
    expect(wrapper.find(".error-stub").exists()).toBe(true);
    expect(wrapper.text()).toContain("Something went wrong");
    expect(wrapper.html()).not.toContain("Hidden");
  });

  it("renders header as NuxtLink when headerLink is provided", () => {
    const wrapper = mount(LandingCardShell, {
      props: { ...defaultProps, headerLink: "/search?type=Instruments" },
      global: { stubs },
    });
    const link = wrapper.find(".nuxt-link");
    expect(link.exists()).toBe(true);
    expect(link.attributes("href")).toBe("/search?type=Instruments");
  });

  it("renders header as div when no headerLink", () => {
    const wrapper = mount(LandingCardShell, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.find(".nuxt-link").exists()).toBe(false);
  });

  it("applies headerClass to title element", () => {
    const wrapper = mount(LandingCardShell, {
      props: { ...defaultProps, headerClass: "text-left md:whitespace-nowrap" },
      global: { stubs },
    });
    const h2 = wrapper.find("h2");
    expect(h2.classes()).toContain("card-title");
    expect(h2.classes()).toContain("text-left");
  });
});
