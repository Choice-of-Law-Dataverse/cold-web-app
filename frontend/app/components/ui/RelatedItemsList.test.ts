import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import RelatedItemsList from "./RelatedItemsList.vue";

describe("RelatedItemsList", () => {
  const mockItems = [
    { id: "1", title: "Item 1" },
    { id: "2", title: "Item 2" },
    { id: "3", title: "Item 3" },
  ];

  it("renders items when provided", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
      },
    });
    expect(wrapper.text()).toContain("Item 1");
    expect(wrapper.text()).toContain("Item 2");
    expect(wrapper.text()).toContain("Item 3");
  });

  it("shows loading state when isLoading is true", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: [],
        isLoading: true,
        basePath: "/test",
      },
    });
    expect(wrapper.findComponent({ name: "LoadingBar" }).exists()).toBe(true);
  });

  it("displays only first 10 items initially when more than 10 items", () => {
    const manyItems = Array.from({ length: 15 }, (_, i) => ({
      id: `${i + 1}`,
      title: `Item ${i + 1}`,
    }));

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: manyItems,
        basePath: "/test",
      },
    });

    expect(wrapper.text()).toContain("Item 1");
    expect(wrapper.text()).toContain("Item 10");
    expect(wrapper.text()).not.toContain("Item 11");
  });

  it("shows 'Show more' button when more than 10 items", () => {
    const manyItems = Array.from({ length: 15 }, (_, i) => ({
      id: `${i + 1}`,
      title: `Item ${i + 1}`,
    }));

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: manyItems,
        basePath: "/test",
      },
    });

    expect(wrapper.findComponent({ name: "ShowMoreLess" }).exists()).toBe(true);
  });

  it("does not show button when 10 or fewer items", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
      },
    });

    expect(wrapper.findComponent({ name: "ShowMoreLess" }).exists()).toBe(
      false,
    );
  });

  it("toggles to show all items when clicking show more", async () => {
    const manyItems = Array.from({ length: 15 }, (_, i) => ({
      id: `${i + 1}`,
      title: `Item ${i + 1}`,
    }));

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: manyItems,
        basePath: "/test",
      },
    });

    expect(wrapper.text()).not.toContain("Item 11");

    const showMoreLess = wrapper.findComponent({ name: "ShowMoreLess" });
    const button = showMoreLess.find("button");
    await button.trigger("click");

    expect(wrapper.text()).toContain("Item 11");
    expect(wrapper.text()).toContain("Item 15");
  });

  it("hides extra items when clicking show less", async () => {
    const manyItems = Array.from({ length: 15 }, (_, i) => ({
      id: `${i + 1}`,
      title: `Item ${i + 1}`,
    }));

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: manyItems,
        basePath: "/test",
      },
    });

    const showMoreLess = wrapper.findComponent({ name: "ShowMoreLess" });
    await showMoreLess.find("button").trigger("click"); // Show all
    await showMoreLess.find("button").trigger("click"); // Show less

    expect(wrapper.text()).not.toContain("Item 11");
  });

  it("constructs correct link paths with basePath", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/questions",
      },
    });

    // Check that links are constructed correctly in the HTML
    const html = wrapper.html();
    expect(html).toContain("/questions/1");
    expect(html).toContain("/questions/2");
  });

  it("uses item id as path when it starts with slash", () => {
    const itemsWithPaths = [
      { id: "/absolute/path/1", title: "Item 1" },
      { id: "relative/2", title: "Item 2" },
    ];

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: itemsWithPaths,
        basePath: "/base",
      },
    });

    const html = wrapper.html();
    expect(html).toContain("/absolute/path/1");
    expect(html).toContain("/base/relative/2");
  });

  it("displays empty fallback when no items and action is display", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: [],
        basePath: "/test",
        emptyValueBehavior: {
          action: "display",
          fallback: "—",
        },
      },
    });

    expect(wrapper.text()).toContain("—");
  });

  it("hides component when no items and action is not display", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: [],
        basePath: "/test",
        emptyValueBehavior: {
          action: "hide",
          fallback: "Should not see this",
        },
      },
    });

    expect(wrapper.text()).not.toContain("Should not see this");
  });

  it("applies link-chip--neutral class to items", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
      },
    });

    expect(wrapper.html()).toContain("link-chip--neutral");
  });

  it("applies link-chip--action class to show more button", () => {
    const manyItems = Array.from({ length: 15 }, (_, i) => ({
      id: `${i + 1}`,
      title: `Item ${i + 1}`,
    }));

    const wrapper = mount(RelatedItemsList, {
      props: {
        items: manyItems,
        basePath: "/test",
      },
    });

    const showMoreLess = wrapper.findComponent({ name: "ShowMoreLess" });
    expect(showMoreLess.props("buttonClass")).toBe("link-chip--action");
  });

  it("applies link-chip--neutral regardless of entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "court decision",
      },
    });

    expect(wrapper.html()).toContain("link-chip--neutral");
    expect(wrapper.html()).not.toContain("link-chip--court-decision");
  });
});
