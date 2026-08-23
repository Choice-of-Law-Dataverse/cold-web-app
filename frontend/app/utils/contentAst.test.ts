import { describe, it, expect } from "vitest";
import {
  extractHeadingSections,
  nodeText,
  type ContentNode,
} from "./contentAst";

const BODY: ContentNode[] = [
  ["h2", { id: "a" }, "What is party autonomy?"],
  ["iframe", { src: "https://youtube.com/embed/x" }],
  [
    "p",
    {},
    "Party autonomy is the power to ",
    ["strong", {}, "choose"],
    " a law.",
  ],
  ["h2", { id: "b" }, "Video only question"],
  ["iframe", { src: "https://youtube.com/embed/y" }],
  ["h2", { id: "c" }, "Two paragraphs"],
  ["p", {}, "First."],
  ["p", {}, "Second."],
];

describe("nodeText", () => {
  it("flattens nested inline nodes", () => {
    expect(nodeText(["p", {}, "a ", ["em", {}, "b"], " c"])).toBe("a b c");
  });

  it("ignores embeds that carry no readable text", () => {
    expect(nodeText(["iframe", { src: "x" }])).toBe("");
    expect(nodeText(["p", {}, "text", ["img", { alt: "icon" }]])).toBe("text");
  });
});

describe("extractHeadingSections", () => {
  it("pairs each heading with the text that follows it", () => {
    const sections = extractHeadingSections(BODY);
    expect(sections).toEqual([
      {
        heading: "What is party autonomy?",
        text: "Party autonomy is the power to choose a law.",
      },
      { heading: "Video only question", text: "" },
      { heading: "Two paragraphs", text: "First. Second." },
    ]);
  });

  it("returns nothing for a missing or malformed body", () => {
    expect(extractHeadingSections(null)).toEqual([]);
    expect(extractHeadingSections(undefined)).toEqual([]);
  });

  it("skips content that appears before the first heading", () => {
    expect(
      extractHeadingSections([
        ["p", {}, "intro"],
        ["h2", {}, "H"],
        ["p", {}, "body"],
      ]),
    ).toEqual([{ heading: "H", text: "body" }]);
  });
});
