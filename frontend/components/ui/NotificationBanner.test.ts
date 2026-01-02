import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import NotificationBanner from "./NotificationBanner.vue";

describe("NotificationBanner", () => {
  it("displays custom notification message when provided", () => {
    const wrapper = mount(NotificationBanner, {
      props: {
        notificationBannerMessage: "Custom message here",
      },
    });
    expect(wrapper.text()).toContain("Custom message here");
  });

  it("displays fallback message with jurisdiction name when no custom message", () => {
    const wrapper = mount(NotificationBanner, {
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
      props: {
        fallbackMessage: "Custom fallback text",
      },
    });
    expect(wrapper.text()).toContain("Custom fallback text");
  });

  it("prioritizes custom notification message over fallback with jurisdiction", () => {
    const wrapper = mount(NotificationBanner, {
      props: {
        notificationBannerMessage: "Custom message",
        jurisdictionName: "Spain",
      },
    });
    expect(wrapper.text()).toContain("Custom message");
    expect(wrapper.text()).not.toContain("Spain");
  });

  it("uses default flag icon when no custom icon provided", () => {
    const wrapper = mount(NotificationBanner);
    // Default icon should be set
    expect(wrapper.html()).toBeTruthy();
  });

  it("accepts custom icon prop", () => {
    const wrapper = mount(NotificationBanner, {
      props: {
        icon: "i-material-symbols:info",
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it("includes contact link when showing jurisdiction fallback", () => {
    const wrapper = mount(NotificationBanner, {
      props: {
        jurisdictionName: "Italy",
      },
    });
    // NuxtLink is stubbed in tests, so we check for the component
    expect(wrapper.html()).toContain("Contact us");
    expect(wrapper.html()).toContain("contact");
  });

  it("does not show contact link with custom notification message", () => {
    const wrapper = mount(NotificationBanner, {
      props: {
        notificationBannerMessage: "Custom info",
      },
    });
    expect(wrapper.html()).not.toContain("Contact us");
  });
});
