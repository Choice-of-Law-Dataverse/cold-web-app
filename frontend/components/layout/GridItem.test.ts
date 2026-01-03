import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import GridItem from "./GridItem.vue";

describe("GridItem", () => {
  it("renders with default 12 columns", () => {
    const wrapper = mount(GridItem);
    expect(wrapper.classes()).toContain("col-span-12");
  });

  it("renders with custom column count", () => {
    const wrapper = mount(GridItem, {
      props: {
        cols: 6,
      },
    });
    expect(wrapper.classes()).toContain("col-span-6");
  });

  it("renders with md responsive column count", () => {
    const wrapper = mount(GridItem, {
      props: {
        cols: 12,
        mdCols: 6,
      },
    });
    expect(wrapper.classes()).toContain("col-span-12");
    expect(wrapper.classes()).toContain("md:col-span-6");
  });

  it("renders with lg responsive column count", () => {
    const wrapper = mount(GridItem, {
      props: {
        cols: 12,
        lgCols: 4,
      },
    });
    expect(wrapper.classes()).toContain("col-span-12");
    expect(wrapper.classes()).toContain("lg:col-span-4");
  });

  it("renders with all responsive breakpoints", () => {
    const wrapper = mount(GridItem, {
      props: {
        cols: 12,
        mdCols: 6,
        lgCols: 4,
      },
    });
    expect(wrapper.classes()).toContain("col-span-12");
    expect(wrapper.classes()).toContain("md:col-span-6");
    expect(wrapper.classes()).toContain("lg:col-span-4");
  });

  it("renders slot content", () => {
    const wrapper = mount(GridItem, {
      slots: {
        default: "Grid content",
      },
    });
    expect(wrapper.text()).toContain("Grid content");
  });

  it("accepts string column values", () => {
    const wrapper = mount(GridItem, {
      props: {
        cols: "8",
      },
    });
    expect(wrapper.classes()).toContain("col-span-8");
  });

  it("validates column count between 1 and 12", () => {
    const validator = GridItem.props.cols.validator;
    expect(validator(1)).toBe(true);
    expect(validator(12)).toBe(true);
    expect(validator(6)).toBe(true);
    expect(validator(0)).toBe(false);
    expect(validator(13)).toBe(false);
  });

  it("validates md column count between 1 and 12 or null", () => {
    const validator = GridItem.props.mdCols.validator;
    expect(validator(null)).toBe(true);
    expect(validator(1)).toBe(true);
    expect(validator(12)).toBe(true);
    expect(validator(0)).toBe(false);
    expect(validator(13)).toBe(false);
  });

  it("validates lg column count between 1 and 12 or null", () => {
    const validator = GridItem.props.lgCols.validator;
    expect(validator(null)).toBe(true);
    expect(validator(1)).toBe(true);
    expect(validator(12)).toBe(true);
    expect(validator(0)).toBe(false);
    expect(validator(13)).toBe(false);
  });
});
