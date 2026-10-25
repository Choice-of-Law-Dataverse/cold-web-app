import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import SaveModal from "./SaveModal.vue";

const stubs = {
  UModal: { template: "<div><slot name='content' /></div>" },
  UFormField: { template: "<div><slot name='label' /><slot /></div>" },
  UTextarea: { template: "<textarea />" },
  UIcon: true,
  UAlert: {
    props: ["title"],
    template: "<div role='alert'>{{ title }}</div>",
  },
};

function mountModal(props: Record<string, unknown> = {}) {
  return mount(SaveModal, {
    props: { open: true, ...props },
    global: { stubs },
  });
}

describe("SaveModal", () => {
  it("asks the parent to submit without closing itself", async () => {
    const wrapper = mountModal();

    await wrapper.get("[data-testid='save-modal-submit']").trigger("click");

    expect(wrapper.emitted("submit")).toHaveLength(1);
    expect(wrapper.emitted("update:open")).toBeUndefined();
  });

  it("shows the submission error", () => {
    const wrapper = mountModal({ error: "Could not submit" });

    expect(wrapper.get("[role='alert']").text()).toBe("Could not submit");
  });

  it("disables submitting while a request is in flight", () => {
    const wrapper = mountModal({ submitting: true });
    const button = wrapper.get("[data-testid='save-modal-submit']");

    expect(button.attributes("disabled")).toBeDefined();
    expect(button.text()).toContain("Submitting");
  });

  it("closes when going back", async () => {
    const wrapper = mountModal();

    await wrapper.get("button.gray-link").trigger("click");

    expect(wrapper.emitted("update:open")).toEqual([[false]]);
  });
});
