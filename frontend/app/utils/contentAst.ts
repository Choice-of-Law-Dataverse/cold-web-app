/**
 * Nuxt Content stores a parsed page body as nested `[tag, props, ...children]`
 * tuples, where a child is either a plain string or another tuple.
 */
export type ContentNode =
  string | [string, Record<string, unknown>, ...ContentNode[]];

export interface ContentSection {
  heading: string;
  text: string;
}

const IGNORED_TAGS = new Set(["iframe", "img", "script", "style"]);

/** Concatenates the visible text of a node and everything nested inside it. */
export function nodeText(node: ContentNode): string {
  if (typeof node === "string") return node;
  if (!Array.isArray(node)) return "";

  const [tag, , ...children] = node;
  if (IGNORED_TAGS.has(tag)) return "";

  return children.map(nodeText).join("");
}

/**
 * Groups a content body into sections introduced by a heading.
 *
 * Used to derive FAQ and glossary structured data from the same markdown the
 * page renders, so the two cannot drift apart.
 */
export function extractHeadingSections(
  nodes: ContentNode[] | null | undefined,
  headingTag = "h2",
): ContentSection[] {
  if (!Array.isArray(nodes)) return [];

  const sections: ContentSection[] = [];
  let current: ContentSection | null = null;

  for (const node of nodes) {
    if (!Array.isArray(node)) continue;

    if (node[0] === headingTag) {
      if (current) sections.push(current);
      current = { heading: nodeText(node).trim(), text: "" };
      continue;
    }

    if (!current) continue;

    const text = nodeText(node).trim();
    if (!text) continue;
    current.text = current.text ? `${current.text} ${text}` : text;
  }

  if (current) sections.push(current);

  return sections.filter((section) => section.heading !== "");
}
