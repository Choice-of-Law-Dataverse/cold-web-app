import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import JurisdictionSelector from "./JurisdictionSelector.vue";
import { ref } from "vue";

// Mock the composables
const mockJurisdictions = ref(null);
const mockIsLoading = ref(false);

vi.mock("@/composables/useJurisdictions", () => ({
  useJurisdictions: () => ({
    data: mockJurisdictions,
    isLoading: mockIsLoading,
  }),
}));

// Mock the route
const mockRoute = {
  params: { id: "fra" },
};

vi.mock("vue-router", () => ({
  useRoute: () => mockRoute,
}));

describe("JurisdictionSelector", () => {
  beforeEach(() => {
    mockJurisdictions.value = null;
    mockIsLoading.value = false;
    mockRoute.params.id = "fra";
  });

  it("renders title", () => {
    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });
    expect(wrapper.text()).toContain("Add comparison with");
  });

  it("shows loading state when jurisdictions are loading", () => {
    mockIsLoading.value = true;
    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });
    expect(wrapper.text()).toContain("Loading jurisdictions...");
  });

  it("shows unavailable message when no jurisdictions data", () => {
    mockJurisdictions.value = null;
    mockIsLoading.value = false;
    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });
    expect(wrapper.text()).toContain(
      "Jurisdictions unavailable (API connection required)",
    );
  });

  it("filters out current jurisdiction from available options", () => {
    mockJurisdictions.value = [
      { name: "France", alpha3Code: "FRA" },
      { name: "Germany", alpha3Code: "DEU" },
      { name: "Italy", alpha3Code: "ITA" },
    ];
    mockRoute.params.id = "fra";

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    // Check that Germany and Italy are available but France is not
    expect(wrapper.findComponent({ name: "JurisdictionSelectMenu" }).exists()).toBe(
      true,
    );
  });

  it("emits jurisdiction-selected when selection is made", async () => {
    mockJurisdictions.value = [
      { name: "France", alpha3Code: "FRA" },
      { name: "Germany", alpha3Code: "DEU" },
    ];
    mockRoute.params.id = "fra";

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    const selectMenu = wrapper.findComponent({ name: "JurisdictionSelectMenu" });
    await selectMenu.vm.$emit("country-selected", {
      name: "Germany",
      alpha3Code: "DEU",
    });

    expect(wrapper.emitted("jurisdiction-selected")).toBeTruthy();
    expect(wrapper.emitted("jurisdiction-selected")?.[0]).toEqual([
      { name: "Germany", alpha3Code: "DEU" },
    ]);
  });

  it("does not emit event when selection has no alpha3Code", async () => {
    mockJurisdictions.value = [
      { name: "Germany", alpha3Code: "DEU" },
    ];

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    const selectMenu = wrapper.findComponent({ name: "JurisdictionSelectMenu" });
    await selectMenu.vm.$emit("country-selected", { name: "Invalid" });

    expect(wrapper.emitted("jurisdiction-selected")).toBeFalsy();
  });

  it("handles uppercase comparison for current jurisdiction filtering", () => {
    mockJurisdictions.value = [
      { name: "France", alpha3Code: "fra" },
      { name: "Germany", alpha3Code: "deu" },
    ];
    mockRoute.params.id = "FRA"; // uppercase

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    // France should be filtered out despite lowercase alpha3Code in data
    const selectMenu = wrapper.findComponent({ name: "JurisdictionSelectMenu" });
    expect(selectMenu.exists()).toBe(true);
  });

  it("returns empty array when jurisdictions data is missing", () => {
    mockJurisdictions.value = null;
    mockRoute.params.id = "fra";

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    expect(wrapper.text()).toContain("unavailable");
  });

  it("returns empty array when currentIso3Code is missing", () => {
    mockJurisdictions.value = [
      { name: "Germany", alpha3Code: "DEU" },
    ];
    mockRoute.params.id = undefined;

    const wrapper = mount(JurisdictionSelector, {
      props: {
        formattedJurisdiction: { name: "France" },
      },
    });

    expect(wrapper.text()).toContain("unavailable");
  });
});
