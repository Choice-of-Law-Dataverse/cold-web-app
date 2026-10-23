import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { z } from "zod";

const push = vi.fn();
const post = vi.fn();

vi.mock("#imports", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/composables/useApiClient", () => ({
  useApiClient: () => ({ client: { POST: post } }),
}));

const {
  useSuggestionForm,
  SUBMISSION_FAILED_MESSAGE,
  SUBMISSION_RECEIVED_MESSAGE,
  SUBMISSION_SOURCE,
} = await import("./useSuggestionForm");

function setup() {
  const abbreviation = ref("");
  const form = useSuggestionForm({
    endpoint: "/suggestions/regional-instruments",
    schema: z.object({
      abbreviation: z
        .string()
        .min(1, { error: "Abbreviation is required" })
        .min(3, { error: "Abbreviation must be at least 3 characters long" }),
    }),
    values: () => ({ abbreviation: abbreviation.value }),
    payload: () => ({ abbreviation: abbreviation.value }),
  });
  return { abbreviation, form };
}

describe("useSuggestionForm", () => {
  beforeEach(() => {
    push.mockReset();
    post.mockReset();
  });

  it("keeps the modal closed and shows the first error per field when invalid", () => {
    const { form } = setup();

    form.openSaveModal();

    expect(form.isSaveModalOpen.value).toBe(false);
    expect(form.errors.value).toEqual({
      abbreviation: "Abbreviation is required",
    });
  });

  it("opens the modal and clears errors once the form is valid", () => {
    const { abbreviation, form } = setup();
    form.openSaveModal();
    abbreviation.value = "EU";
    form.openSaveModal();
    expect(form.errors.value.abbreviation).toMatch(/at least 3/u);

    abbreviation.value = "Rome I";
    form.openSaveModal();

    expect(form.isSaveModalOpen.value).toBe(true);
    expect(form.errors.value).toEqual({});
  });

  it("posts the payload with comments and source, then redirects", async () => {
    post.mockResolvedValue({ data: {}, error: undefined });
    const { abbreviation, form } = setup();
    abbreviation.value = "Rome I";
    form.openSaveModal();
    form.comments.value = "Please add";

    await form.submit();

    expect(post).toHaveBeenCalledWith("/suggestions/regional-instruments", {
      body: { abbreviation: "Rome I", submitter_comments: "Please add" },
      params: { header: { source: SUBMISSION_SOURCE } },
    });
    expect(form.isSaveModalOpen.value).toBe(false);
    expect(form.submitError.value).toBe("");
    expect(push).toHaveBeenCalledWith({
      path: "/confirmation",
      query: { message: SUBMISSION_RECEIVED_MESSAGE },
    });
  });

  it("omits empty comments", async () => {
    post.mockResolvedValue({ data: {}, error: undefined });
    const { abbreviation, form } = setup();
    abbreviation.value = "Rome I";

    await form.submit();

    expect(post.mock.calls[0]?.[1].body).toEqual({
      abbreviation: "Rome I",
      submitter_comments: undefined,
    });
  });

  it.each([
    [
      "an error response",
      () => post.mockResolvedValue({ error: { detail: "x" } }),
    ],
    ["a network failure", () => post.mockRejectedValue(new Error("offline"))],
  ])("keeps the modal open with a message after %s", async (_, arrange) => {
    arrange();
    const { abbreviation, form } = setup();
    abbreviation.value = "Rome I";
    form.openSaveModal();

    await form.submit();

    expect(form.isSaveModalOpen.value).toBe(true);
    expect(form.isSubmitting.value).toBe(false);
    expect(form.submitError.value).toBe(SUBMISSION_FAILED_MESSAGE);
    expect(push).not.toHaveBeenCalled();
  });

  it("ignores a second submit while the first is in flight", async () => {
    let resolve: (value: { error: undefined }) => void = () => {};
    post.mockReturnValue(new Promise((r) => (resolve = r)));
    const { abbreviation, form } = setup();
    abbreviation.value = "Rome I";

    const first = form.submit();
    await form.submit();
    resolve({ error: undefined });
    await first;

    expect(post).toHaveBeenCalledTimes(1);
  });

  it("returns home on cancel", async () => {
    const { form } = setup();
    await form.cancel();
    expect(push).toHaveBeenCalledWith("/");
  });
});
