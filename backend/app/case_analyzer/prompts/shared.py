NAV_TOOLS_PREAMBLE = """

Use the navigation tools to locate relevant passages in the court decision:
- list_headings() — see the document's structure
- search(query) — find paragraphs matching a query
- read_paragraphs(start_paragraph, count) — read a search hit and adjacent numbered paragraphs
- read_section(heading) — read a detected section by name
- read_window(anchor, chars_before, chars_after) — read context around a specific phrase
- get_paragraph_containing(snippet) — get the full paragraph containing a text snippet
- read_head(n_chars) — read the beginning of the document
- read_tail(n_chars) — read the end of the document

MULTILINGUAL RETRIEVAL:
- Court decisions may be written in any language or contain more than one language. Infer the actual source language(s)
  from read_head() and list_headings(); never assume the language from the jurisdiction alone.
- Search in every source language used by the decision. Translate each legal concept into that language and try
  multiple local legal terms, synonyms, inflections, statute names, and common abbreviations; an English-only search
  is insufficient unless the relevant passages are in English.
- For exhaustive or negative findings, do not stop after one query. Inspect headings and run several conceptually
  distinct source-language searches, then read the matching and adjacent paragraphs before concluding.
- Navigation results preserve the source text. Quote extracted passages verbatim in their original language and only
  translate fields whose output contract requires English.
"""
