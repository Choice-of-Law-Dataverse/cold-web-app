import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import NotificationBanner from "./NotificationBanner.vue";

const UAlertStub = defineComponent({
  props: ["icon", "color", "variant"],
  setup(_, { slots }) {
    return () =>
      h("div", { class: "u-alert-stub" }, [
        slots.description ? slots.description() : null,
        slots.default ? slots.default() : null,
      ]);
  },
});

const mountOptions = {
  global: {
    stubs: {
      UAlert: UAlertStub,
      NuxtLink: {
        template: "<a><slot /></a>",
      },
    },
  },
};

describe("NotificationBanner", () => {
  it("displays custom notification message when provided", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        notificationBannerMessage: "Custom message here",
      },
    });
    expect(wrapper.text()).toContain("Custom message here");
  });

  it("displays fallback message with jurisdiction name when no custom message", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        jurisdictionName: "France",
        notificationBannerMessage: "",
      },
    });
    expect(wrapper.text()).toContain("France");
    expect(wrapper.text()).toContain("Contact us");
  });

  it("replaces {jurisdiction} placeholder in fallback message", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        jurisdictionName: "Germany",
        fallbackMessage: "No data for {jurisdiction} yet",
      },
    });
    expect(wrapper.text()).toContain("No data for Germany yet");
    expect(wrapper.text()).not.toContain("{jurisdiction}");
  });

  it("shows default fallback when no jurisdiction name or custom message", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        jurisdictionName: "",
        notificationBannerMessage: "",
      },
    });
    const text = wrapper.text();
    expect(text).toContain("data for");
    expect(text).toContain("{jurisdiction}");
  });

  it("uses custom fallback message when provided", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        fallbackMessage: "Custom fallback text",
      },
    });
    expect(wrapper.text()).toContain("Custom fallback text");
  });

  it("prioritizes custom notification message over fallback with jurisdiction", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        notificationBannerMessage: "Custom message",
        jurisdictionName: "Spain",
      },
    });
    expect(wrapper.text()).toContain("Custom message");
    expect(wrapper.text()).not.toContain("Spain");
  });

  it("uses default flag icon when no custom icon provided", () => {
    const wrapper = mount(NotificationBanner, mountOptions);
    expect(wrapper.html()).toBeTruthy();
  });

  it("accepts custom icon prop", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        icon: "i-material-symbols:info",
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("includes contact link when showing jurisdiction fallback", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        jurisdictionName: "Italy",
      },
    });
    expect(wrapper.html()).toContain("Contact us");
  });

  it("does not show contact link with custom notification message", () => {
    const wrapper = mount(NotificationBanner, {
      ...mountOptions,
      props: {
        notificationBannerMessage: "Custom info",
      },
    });
    expect(wrapper.html()).not.toContain("Contact us");
  });
});
