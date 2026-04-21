NAV_TOOLS_PREAMBLE = """

Use the navigation tools to locate relevant passages in the court decision:
- list_headings() — see the document's structure
- search(query) — find paragraphs matching a query
- read_section(heading) — read a detected section by name
- read_window(anchor, chars_before, chars_after) — read context around a specific phrase
- get_paragraph_containing(snippet) — get the full paragraph containing a text snippet
- read_head(n_chars) — read the beginning of the document
- read_tail(n_chars) — read the end of the document
"""
