import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import QuestionJurisdictions from "./QuestionJurisdictions.vue";
import { ref } from "vue";

// Mock the composable
const mockQuestionData = ref<{
  answers: unknown[];
  questionTitle?: string;
} | null>(null);
const mockIsLoading = ref(false);
const mockError = ref<Error | null>(null);

vi.mock("@/composables/useQuestionCountries", () => ({
  useQuestionCountries: () => ({
    data: mockQuestionData,
    isLoading: mockIsLoading,
    error: mockError,
  }),
}));

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
    expect(buttons[0].classes()).toContain("region-badge-active");
  });

  it("changes selected region when clicking different region button", async () => {
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const buttons = wrapper.findAll(".region-badge");
    await buttons[1].trigger("click");
    expect(buttons[1].classes()).toContain("region-badge-active");
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
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Yes",
          Jurisdictions: "France",
          "Jurisdictions Alpha-3 code": "FRA",
        },
        {
          Answer: "No data",
          Jurisdictions: "Spain",
          "Jurisdictions Alpha-3 code": "ESP",
        },
        {
          Answer: "Nothing found",
          Jurisdictions: "Italy",
          "Jurisdictions Alpha-3 code": "ITA",
        },
        {
          Answer: "No information",
          Jurisdictions: "Germany",
          "Jurisdictions Alpha-3 code": "DEU",
        },
      ],
    };
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
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Maybe",
          Jurisdictions: "Country1",
          "Jurisdictions Alpha-3 code": "C01",
        },
        {
          Answer: "No",
          Jurisdictions: "Country2",
          "Jurisdictions Alpha-3 code": "C02",
        },
        {
          Answer: "Not applicable",
          Jurisdictions: "Country3",
          "Jurisdictions Alpha-3 code": "C03",
        },
        {
          Answer: "Yes",
          Jurisdictions: "Country4",
          "Jurisdictions Alpha-3 code": "C04",
        },
      ],
    };
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    // First should be region selector, then answers
    const firstAnswerRow = detailRows[1];
    expect(firstAnswerRow.props("label")).toBe("Yes");
  });

  it("sorts remaining answers alphabetically after priority answers", () => {
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Zebra",
          Jurisdictions: "Country1",
          "Jurisdictions Alpha-3 code": "C01",
        },
        {
          Answer: "Apple",
          Jurisdictions: "Country2",
          "Jurisdictions Alpha-3 code": "C02",
        },
        {
          Answer: "Yes",
          Jurisdictions: "Country3",
          "Jurisdictions Alpha-3 code": "C03",
        },
      ],
    };
    const wrapper = mount(QuestionJurisdictions, {
      props: {
        questionSuffix: "/test-question",
      },
    });
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    expect(detailRows[1].props("label")).toBe("Yes");
    expect(detailRows[2].props("label")).toBe("Apple");
    expect(detailRows[3].props("label")).toBe("Zebra");
  });

  it("filters countries by selected region", async () => {
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Yes",
          Jurisdictions: "France",
          "Jurisdictions Alpha-3 code": "FRA",
          "Jurisdictions Region": "Europe",
        },
        {
          Answer: "Yes",
          Jurisdictions: "Japan",
          "Jurisdictions Alpha-3 code": "JPN",
          "Jurisdictions Region": "Asia & Pacific",
        },
      ],
    };
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
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Yes",
          Jurisdictions: "Zambia",
          "Jurisdictions Alpha-3 code": "ZMB",
        },
        {
          Answer: "Yes",
          Jurisdictions: "Argentina",
          "Jurisdictions Alpha-3 code": "ARG",
        },
        {
          Answer: "Yes",
          Jurisdictions: "Brazil",
          "Jurisdictions Alpha-3 code": "BRA",
        },
      ],
    };
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

  it("displays 'No jurisdictions' when no countries for an answer", async () => {
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Yes",
          Jurisdictions: "France",
          "Jurisdictions Alpha-3 code": "FRA",
          "Jurisdictions Region": "Europe",
        },
      ],
    };
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

    expect(wrapper.text()).toContain("No jurisdictions");
  });

  it("renders links with correct paths", async () => {
    mockQuestionData.value = {
      answers: [
        {
          Answer: "Yes",
          Jurisdictions: "France",
          "Jurisdictions Alpha-3 code": "FRA",
        },
      ],
    };
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
