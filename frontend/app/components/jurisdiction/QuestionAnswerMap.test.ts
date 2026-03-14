import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { defineComponent, h, ref } from "vue";
import QuestionAnswerMap from "./QuestionAnswerMap.vue";
import type {
  QuestionJurisdictionsData,
  Jurisdiction,
} from "@/composables/useQuestionJurisdictions";

const mockQuestionData = ref<QuestionJurisdictionsData | null>(null);
const mockIsLoading = ref(false);
const mockError = ref<Error | null>(null);

vi.mock("@/composables/useQuestionJurisdictions", () => ({
  useQuestionJurisdictions: () => ({
    data: mockQuestionData,
    isLoading: mockIsLoading,
    error: mockError,
  }),
}));

const UCardStub = defineComponent({
  name: "UCard",
  setup(_props, { slots }) {
    return () =>
      h("div", { class: "card-stub" }, [
        slots.header
          ? h("div", { class: "card-header" }, slots.header())
          : null,
        slots.default?.(),
      ]);
  },
});

const USelectStub = defineComponent({
  name: "USelect",
  props: ["modelValue", "items", "size", "icon", "class"],
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    return () =>
      h(
        "select",
        {
          class: "select-stub",
          value: props.modelValue,
          onChange: (e: Event) =>
            emit("update:modelValue", (e.target as HTMLSelectElement).value),
        },
        (props.items || []).map((item: string) =>
          h("option", { value: item, key: item }, item),
        ),
      );
  },
});

function createJurisdiction(
  name: string,
  code: string,
  region = "",
): Jurisdiction {
  return { name, code, region };
}

function createQuestionData(
  answersWithJurisdictions: Array<{
    answer: string;
    jurisdictions: Array<{ name: string; code: string; region?: string }>;
  }>,
): QuestionJurisdictionsData {
  const answers: string[] = [];
  const answerGroups = new Map<string, Jurisdiction[]>();

  for (const { answer, jurisdictions } of answersWithJurisdictions) {
    answers.push(answer);
    answerGroups.set(
      answer,
      jurisdictions.map((j) =>
        createJurisdiction(j.name, j.code, j.region || ""),
      ),
    );
  }

  return { questionTitle: "Test Question", answers, answerGroups };
}

const stubs = {
  UCard: UCardStub,
  USelect: USelectStub,
};

function mountComponent(questionSuffix = "/test-question") {
  return mount(QuestionAnswerMap, {
    props: { questionSuffix },
    global: { stubs },
  });
}

async function selectRegion(wrapper: ReturnType<typeof mount>, region: string) {
  const select = wrapper.findComponent(USelectStub);
  select.vm.$emit("update:modelValue", region);
  await wrapper.vm.$nextTick();
}

describe("QuestionAnswerMap", () => {
  beforeEach(() => {
    mockQuestionData.value = null;
    mockIsLoading.value = false;
    mockError.value = null;
  });

  it("renders the region select with 'All' as default", () => {
    const wrapper = mountComponent();
    const select = wrapper.findComponent(USelectStub);
    expect(select.exists()).toBe(true);
    expect(select.props("modelValue")).toBe("All");
  });

  it("shows loading state when data is loading", () => {
    mockIsLoading.value = true;
    const wrapper = mountComponent();
    expect(wrapper.text()).toContain("Loading jurisdictions...");
  });

  it("shows error state when there is an error", () => {
    mockError.value = new Error("Failed to load");
    const wrapper = mountComponent();
    expect(wrapper.text()).toContain("Error loading jurisdictions");
  });

  it("excludes 'No data', 'Nothing found', and 'No information' answers", () => {
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", jurisdictions: [{ name: "France", code: "FRA" }] },
    ]);
    const wrapper = mountComponent();
    expect(wrapper.text()).toContain("Yes");
    expect(wrapper.text()).not.toContain("No data");
    expect(wrapper.text()).not.toContain("Nothing found");
    expect(wrapper.text()).not.toContain("No information");
  });

  it("prioritizes Yes, No, Not applicable answers in order", () => {
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", jurisdictions: [{ name: "Country4", code: "C04" }] },
      { answer: "No", jurisdictions: [{ name: "Country2", code: "C02" }] },
      {
        answer: "Not applicable",
        jurisdictions: [{ name: "Country3", code: "C03" }],
      },
      { answer: "Maybe", jurisdictions: [{ name: "Country1", code: "C01" }] },
    ]);
    const wrapper = mountComponent();
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    expect(detailRows[0]?.props("label")).toBe("Yes");
  });

  it("sorts remaining answers alphabetically after priority answers", () => {
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", jurisdictions: [{ name: "Country3", code: "C03" }] },
      { answer: "Apple", jurisdictions: [{ name: "Country2", code: "C02" }] },
      { answer: "Zebra", jurisdictions: [{ name: "Country1", code: "C01" }] },
    ]);
    const wrapper = mountComponent();
    const detailRows = wrapper.findAllComponents({ name: "DetailRow" });
    expect(detailRows[0]?.props("label")).toBe("Yes");
    expect(detailRows[1]?.props("label")).toBe("Apple");
    expect(detailRows[2]?.props("label")).toBe("Zebra");
  });

  it("filters jurisdictions by selected region", async () => {
    mockQuestionData.value = createQuestionData([
      {
        answer: "Yes",
        jurisdictions: [
          { name: "France", code: "FRA", region: "Europe" },
          { name: "Japan", code: "JPN", region: "Asia & Pacific" },
        ],
      },
    ]);
    const wrapper = mountComponent();

    expect(wrapper.text()).toContain("FRA");
    expect(wrapper.text()).toContain("JPN");

    await selectRegion(wrapper, "Europe");

    expect(wrapper.text()).toContain("FRA");
    expect(wrapper.text()).not.toContain("JPN");
  });

  it("sorts jurisdictions alphabetically within each answer group", () => {
    mockQuestionData.value = createQuestionData([
      {
        answer: "Yes",
        jurisdictions: [
          { name: "Argentina", code: "ARG" },
          { name: "Brazil", code: "BRA" },
          { name: "Zambia", code: "ZMB" },
        ],
      },
    ]);
    const wrapper = mountComponent();
    const text = wrapper.text();
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
        jurisdictions: [{ name: "France", code: "FRA", region: "Europe" }],
      },
    ]);
    const wrapper = mountComponent();

    await selectRegion(wrapper, "Africa");

    expect(wrapper.text()).not.toContain("Yes");
  });

  it("renders links with correct paths", async () => {
    mockQuestionData.value = createQuestionData([
      { answer: "Yes", jurisdictions: [{ name: "France", code: "FRA" }] },
    ]);
    const wrapper = mountComponent();
    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain("FRA/test-question");
  });
});
