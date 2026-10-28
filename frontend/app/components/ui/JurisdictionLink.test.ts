import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import JurisdictionLink from "./JurisdictionLink.vue";

describe("JurisdictionLink", () => {
  it("links to the jurisdiction and shows its flag by default", () => {
    const wrapper = mount(JurisdictionLink, {
      props: { iso3: "FRA", label: "France" },
    });

    const link = wrapper.find("a.entity-link--jurisdiction");
    expect(link.attributes("href")).toBe("/jurisdiction/FRA");
    expect(link.find(".flag-wrapper img").attributes("src")).toMatch(
      /fra\.svg$/,
    );
    expect(link.text()).toContain("France");
  });

  it("links to another entity while keeping the jurisdiction flag", () => {
    const wrapper = mount(JurisdictionLink, {
      props: {
        iso3: "CHE",
        label: "CHE",
        id: "CHE_01-P",
        basePath: "/question",
      },
    });

    const link = wrapper.find("a.entity-link--jurisdiction");
    expect(link.attributes("href")).toBe("/question/CHE_01-P");
    expect(link.find("img").attributes("src")).toMatch(/che\.svg$/);
  });
});
