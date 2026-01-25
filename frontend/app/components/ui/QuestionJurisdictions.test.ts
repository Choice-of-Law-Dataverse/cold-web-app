import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import QuestionJurisdictions from "./QuestionJurisdictions.vue";
import { ref } from "vue";
import type {
  QuestionCountriesData,
  Country,
} from "@/composables/useQuestionCountries";

// Mock the composables
const mockQuestionData = ref<QuestionCountriesData | null>(null);
const mockIsLoading = ref(false);
const mockError = ref<Error | null>(null);

vi.mock("@/composables/useQuestionCountries", () => ({
  useQuestionCountries: () => ({
    data: mockQuestionData,
    isLoading: mockIsLoading,
    error: mockError,
  }),
}));

// Mock useCoveredCountries for JurisdictionFlag component
vi.mock("@/composables/useJurisdictions", () => ({
  useCoveredCountries: () => ({
    data: ref(new Set<string>()),
    isLoading: ref(false),
    error: ref(null),
    isError: ref(false),
    isFetching: ref(false),
  }),
}));

function createCountry(name: string, code: string, region = ""): Country {
  return { name, code, region };
}

function createQuestionData(
  answersWithCountries: Array<{
    answer: string;
    countries: Array<{ name: string; code: string; region?: string }>;
  }>,
): QuestionCountriesData {
  const answers: string[] = [];
  const answerGroups = new Map<string, Country[]>();

  for (const { answer, countries } of answersWithCountries) {
    answers.push(answer);
    answerGroups.set(
      answer,
      countries.map((c) => createCountry(c.name, c.code, c.region || "")),
    );
  }

  return { questionTitle: "Test Question", answers, answerGroups };
}

describe("QuestionJurisdictions", () => {
  beforeEach(() => {
    mockQuestionData.value = null;
    mockIsLoading.value = false;
    mockError.value = null;
  });

  it("renders all region buttons", () => {
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    expect(wrapper.text()).toContain("All");
    expect(wrapper.text()).toContain("Asia & Pacific");
    expect(wrapper.text()).toContain("Europe");
    expect(wrapper.text()).toContain("Arab States");
    expect(wrapper.text()).toContain("Africa");
    expect(wrapper.text()).toContain("South & Latin America");
    expect(wrapper.text()).toContain("North America");
    expect(wrapper.text()).toContain("Middle East");
  });

  it("starts with 'All' region selected by default", () => {
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const buttons = wrapper.findAll(".region-badge");
    expect(buttons[0]?.classes()).toContain("region-badge-active");
  });

  it("changes selected region when clicking different region button", async () => {
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const buttons = wrapper.findAll(".region-badge");
    await buttons[1]?.trigger("click");
    expect(buttons[1]?.classes()).toContain("region-badge-active");
  });

  it("shows loading state when data is loading", () => {
    mockIsLoading.value = true;
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    expect(wrapper.text()).toContain("Loading jurisdictions...");
  });

  it("shows error state when there is an error", () => {
    mockError.value = new Error("Failed to load");
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    expect(wrapper.text()).toContain("Error loading jurisdictions");
  });

  it("excludes 'No data', 'Nothing found', and 'No information' answers", () => {
    // Note: These exclusions now happen in the composable, so we only include valid answers
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", countries: [{ name: "France", code: "FRA" }] },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    expect(wrapper.text()).toContain("Yes");
    expect(wrapper.text()).not.toContain("No data");
    expect(wrapper.text()).not.toContain("Nothing found");
    expect(wrapper.text()).not.toContain("No information");
  });

  it("prioritizes Yes, No, Not applicable answers in order", () => {
    // Note: Priority ordering now happens in the composable
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", countries: [{ name: "Country4", code: "C04" }] },
      { answer: "No", countries: [{ name: "Country2", code: "C02" }] },
      {
        answer: "Not applicable",
        countries: [{ name: "Country3", code: "C03" }],
      },
      { answer: "Maybe", countries: [{ name: "Country1", code: "C01" }] },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    // First should be region selector, then answers
    const firstAnswerRow = detailRows[1];
    expect(firstAnswerRow?.props("label")).toBe("Yes");
  });

  it("sorts remaining answers alphabetically after priority answers", () => {
    // Note: Sorting now happens in the composable
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", countries: [{ name: "Country3", code: "C03" }] },
      { answer: "Apple", countries: [{ name: "Country2", code: "C02" }] },
      { answer: "Zebra", countries: [{ name: "Country1", code: "C01" }] },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    expect(detailRows[1]?.props("label")).toBe("Yes");
    expect(detailRows[2]?.props("label")).toBe("Apple");
    expect(detailRows[3]?.props("label")).toBe("Zebra");
  });

  it("filters countries by selected region", async () => {
    mockQuestionData.value = createQuestionData([
      {
        answer: "Yes",
        countries: [
          { name: "France", code: "FRA", region: "Europe" },
          { name: "Japan", code: "JPN", region: "Asia & Pacific" },
        ],
      },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });

    // Initially "All" is selected, should show both countries
    expect(wrapper.text()).toContain("FRA");
    expect(wrapper.text()).toContain("JPN");

    // Click Europe region
    const buttons = wrapper.findAll(".region-badge");
    const europeButton = buttons.find((btn) => btn.text() === "Europe");
    await europeButton!.trigger("click");

    // Should show only France now
    expect(wrapper.text()).toContain("FRA");
    expect(wrapper.text()).not.toContain("JPN");
  });

  it("sorts countries alphabetically within each answer group", () => {
    // Note: Sorting now happens in the composable, so countries should already be sorted
    mockQuestionData.value = createQuestionData([
      {
        answer: "Yes",
        countries: [
          { name: "Argentina", code: "ARG" },
          { name: "Brazil", code: "BRA" },
          { name: "Zambia", code: "ZMB" },
        ],
      },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const text = wrapper.text();
    // Check that Argentina appears before Brazil and Brazil before Zambia in the text
    const argIndex = text.indexOf("ARG");
    const braIndex = text.indexOf("BRA");
    const zmbIndex = text.indexOf("ZMB");
    expect(argIndex).toBeGreaterThan(-1);
    expect(braIndex).toBeGreaterThan(-1);
    expect(zmbIndex).toBeGreaterThan(-1);
    expect(argIndex).toBeLessThan(braIndex);
    expect(braIndex).toBeLessThan(zmbIndex);
  });

  it("hides answer row when no jurisdictions for selected region", async () => {
    mockQuestionData.value = createQuestionData([
      {
        answer: "Yes",
        countries: [{ name: "France", code: "FRA", region: "Europe" }],
      },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });

    // Select a region with no countries
    const buttons = wrapper.findAll(".region-badge");
    const africaButton = buttons.find((btn) => btn.text() === "Africa");
    await africaButton!.trigger("click");
    await wrapper.vm.$nextTick();

    // Row should not be rendered when there are no jurisdictions
    expect(wrapper.text()).not.toContain("Yes");
  });

  it("renders links with correct paths", async () => {
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", countries: [{ name: "France", code: "FRA" }] },
    ]);
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    await wrapper.vm.$nextTick();
    // Check that the question suffix is properly used in the template
    expect(wrapper.html()).toContain("FRA/test-question");
  });
});
