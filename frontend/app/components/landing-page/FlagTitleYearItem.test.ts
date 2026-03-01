import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import FlagTitleYearItem from "./FlagTitleYearItem.vue";

const stubs = {
  UButton: defineComponent({
    props: ["to", "variant", "color"],
    setup(props, { slots, attrs }) {
      return () =>
        h(
          "a",
          { href: props.to, class: ["u-button-stub", attrs.class] },
          slots.default?.(),
        );
    },
  }),
  JurisdictionFlag: defineComponent({
    props: ["iso3"],
    setup(props) {
      return () => h("span", { class: "flag-stub" }, props.iso3);
    },
  }),
};

describe("FlagTitleYearItem", () => {
  const defaultProps = {
    to: "/court-decision/123",
    iso3: "ARG",
    title: "Case Title v. Defendant",
    year: "2024",
    typeClass: "type-court-decision",
  };

  it("renders title text", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.text()).toContain("Case Title v. Defendant");
  });

  it("renders year text", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.text()).toContain("2024");
  });

  it("applies typeClass to button", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.html()).toContain("type-court-decision");
  });

  it("passes iso3 to JurisdictionFlag", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: defaultProps,
      global: { stubs },
    });
    expect(wrapper.find(".flag-stub").text()).toBe("ARG");
  });

  it("passes to prop to UButton for navigation", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: defaultProps,
      global: { stubs },
    });
    const link = wrapper.find(".u-button-stub");
    expect(link.attributes("href")).toBe("/court-decision/123");
  });

  it("uses empty typeClass by default", () => {
    const wrapper = mount(FlagTitleYearItem, {
      props: { to: "/test", iso3: "USA", title: "Test", year: "2024" },
      global: { stubs },
    });
    expect(wrapper.html()).not.toContain("type-");
  });
});
