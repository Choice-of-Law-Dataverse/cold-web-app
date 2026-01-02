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

    expect(wrapper.text()).toContain("Show more");
  });

  it("does not show button when 10 or fewer items", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
      },
    });

    expect(wrapper.text()).not.toContain("Show more");
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

    const button = wrapper.find("button");
    await button.trigger("click");

    expect(wrapper.text()).toContain("Item 11");
    expect(wrapper.text()).toContain("Item 15");
    expect(wrapper.text()).toContain("Show less");
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

    const button = wrapper.find("button");
    await button.trigger("click"); // Show all
    await button.trigger("click"); // Show less

    expect(wrapper.text()).not.toContain("Item 11");
    expect(wrapper.text()).toContain("Show more");
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
          fallback: "No related items found",
        },
      },
    });

    expect(wrapper.text()).toContain("No related items found");
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

  it("applies court decision badge color for court entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "court decision",
      },
    });

    expect(wrapper.html()).toContain("bg-label-court-decision/10");
  });

  it("applies question badge color for question entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "question",
      },
    });

    expect(wrapper.html()).toContain("bg-label-question/10");
  });

  it("applies instrument badge color for instrument entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "instrument",
      },
    });

    expect(wrapper.html()).toContain("bg-label-instrument/10");
  });

  it("applies literature badge color for literature entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "literature",
      },
    });

    expect(wrapper.html()).toContain("bg-label-literature/10");
  });

  it("applies arbitration badge color for arbitration entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "arbitral award",
      },
    });

    expect(wrapper.html()).toContain("bg-label-arbitration/10");
  });

  it("applies default badge color for unknown entity type", () => {
    const wrapper = mount(RelatedItemsList, {
      props: {
        items: mockItems,
        basePath: "/test",
        entityType: "unknown",
      },
    });

    expect(wrapper.html()).toContain("bg-cold-purple/10");
  });
});
