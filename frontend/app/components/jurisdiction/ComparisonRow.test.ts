import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import ComparisonRow from "./ComparisonRow.vue";
import { ComparisonStateKey } from "./comparisonState";
import { computed, ref } from "vue";

const USkeletonStub = { template: '<div class="u-skeleton-mock"></div>' };
const UIconStub = { template: '<span class="u-icon-mock"></span>', props: ['name', 'title'] };
const UTooltipStub = { template: '<div class="u-tooltip-mock"><slot /></div>', props: ['text', 'disabled'] };

describe("ComparisonRow", () => {
  const defaultRow = {
    id: "01-P",
    question: "Test Question",
    answers: { US: "Yes", UK: "No" },
    matchStatus: "mismatch",
    level: 1,
    theme: "Codification"
  };

  const defaultState = {
    jurisdictions: computed(() => [
      { coldId: "US", name: "United States" },
      { coldId: "UK", name: "United Kingdom" }
    ]),
    answersLoading: ref(false),
    isScrollable: computed(() => false),
    stickyColLeft: computed(() => "0px"),
    allJurisdictionsHaveAnswersLoaded: computed(() => true),
    hasAnswersForJurisdiction: () => true,
    shouldShowDash: (answer: string) => !answer || answer === "Not applicable",
    handleAnswerClick: vi.fn(),
    getAnswerLink: (coldId: string, questionId: string) => `/question/${coldId}_${questionId}`,
    isBoldQuestion: () => false,
  };

  const createWrapper = (rowOverride = {}, stateOverride = {}) => {
    return mount(ComparisonRow, {
      props: {
        row: { ...defaultRow, ...rowOverride } as any,
      },
      global: {
        components: {
          USkeleton: USkeletonStub,
          UIcon: UIconStub,
          UTooltip: UTooltipStub,
        },
        provide: {
          [ComparisonStateKey as symbol]: {
            ...defaultState,
            ...stateOverride,
          },
        },
      },
    });
  };

  it("renders the question cell", () => {
    const wrapper = createWrapper();
    const qCell = wrapper.find(".comparison-cell--question");
    expect(qCell.text()).toContain("Test Question");
    expect(qCell.attributes("style")).toContain("padding-left: 2em;");
  });

  it("renders bold questions", () => {
    const wrapper = createWrapper({}, { isBoldQuestion: (id: string) => id === "01-P" });
    const qCell = wrapper.find(".comparison-cell--question");
    expect(qCell.classes()).toContain("font-semibold");
  });

  it("renders answer cells correctly", () => {
    const wrapper = createWrapper();
    const aCells = wrapper.findAll(".comparison-cell--answer");
    expect(aCells).toHaveLength(2);
    expect(aCells[0].text()).toContain("Yes");
    expect(aCells[1].text()).toContain("No");
  });

  it("displays a dash for 'Not applicable'", () => {
    const wrapper = createWrapper({ answers: { US: "Yes", UK: "Not applicable" } });
    const aCells = wrapper.findAll(".comparison-cell--answer");
    expect(aCells[1].text()).toContain("—");
  });

  it("displays loading skeleton when answers are loading", () => {
    const wrapper = createWrapper({}, {
      answersLoading: ref(true),
      hasAnswersForJurisdiction: () => false
    });
    expect(wrapper.find(".u-skeleton-mock").exists()).toBe(true);
  });

  it("calls handleAnswerClick when clicking an answer", async () => {
    const handleAnswerClick = vi.fn();
    const wrapper = createWrapper({}, { handleAnswerClick });
    
    const answerLink = wrapper.find("a.answer-button");
    await answerLink.trigger("click");
    
    expect(handleAnswerClick).toHaveBeenCalled();
  });
});
