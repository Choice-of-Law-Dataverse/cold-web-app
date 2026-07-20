from .shared import NAV_TOOLS_PREAMBLE

COL_SECTION_PROMPT = (
    """
TASK: Extract all portions of the judgment that discuss choice of law in private international law (PIL) contexts.
INSTRUCTIONS:
1.	Scope of Extraction: Identify and extract the most important paragraphs, sentences, or sections where the court:
-	Determines the choice of law of the parties as per any rules of private international law
-	Discusses "applicable law," "proper law," "governing law," or "choice of law"
-	Analyzes party autonomy in law selection
-	Applies conflict of laws principles
-	References foreign legal systems in determining applicable law
-	Discusses the "closest connection" test or similar PIL methodologies
More specifically, when preparing the output, prioritize: (1) The court's direct conclusions about applicable law, (2) The court's reasoning about choice of law rules, (3) The court's analysis of contractual choice of law clauses, (4) The court's application of PIL principles.
1.1 Make sure to include the following parts:
-	The court's reasoning about law selection and analysis of party agreements on governing law
-	Discussion of PIL principles and application of foreign law provisions
-	Both ratio decidendi and obiter dicta related to choice of law (when present in common-law-style decisions)
-	Jurisdiction discussions ONLY when they directly involve choice of law analysis (e.g., determining which law governs the interpretation of jurisdiction clauses, or how choice of law affects jurisdictional determinations)
-	Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination
1.2 Exclude all of the following:
-	Pure procedural matters unrelated to choice of law
-	Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
-	Enforcement issues not touching on choice of law
-	Other matters on the merit of the dispute unrelated to choice of law or PIL
-	Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis

2.	Extraction Method:
-	Reproduce the court's passages verbatim in the source language (do not paraphrase, do not translate). Use brackets [...] to abbreviate where necessary
-	Extract complete sentences with essential context only
-	Focus primarily on the court's own reasoning and analysis
3.	Quality Check:
-	Ensure each extracted section shows the court's reasoning chain
-	Break longer passages into separate sections if they address different choice of law issues
-	If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list.
4.	CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.
"""
    + NAV_TOOLS_PREAMBLE
)

COL_RETRIEVAL_QUERY_PROMPT = """
TASK: Propose source-language search queries that can locate this judgment's choice-of-law analysis.

Return two to six short queries. Use the actual language or languages visible in the supplied excerpt and headings.
Prefer local legal terms, statutory references, and phrases likely to occur verbatim in this particular judgment.
Cover the court's applicable-law holding and reasoning, not merely jurisdiction or the parties' names.
Do not answer the legal question and do not use external knowledge.
"""

COL_CANDIDATE_AUDIT_PROMPT = """
TASK: Audit every retrieved candidate for choice-of-law relevance.

For every candidate ID supplied below, return exactly one disposition:
- include: the candidate contains material that belongs in the Choice of Law extraction;
- exclude: it is irrelevant, duplicative, purely jurisdictional, or otherwise outside scope;
- needs_additional_context: only while you inspect adjacent paragraphs with the navigation tools.

Before returning the final structured output, resolve every needs_additional_context candidate to include or exclude.
For each included candidate, classify its role and select the exact full paragraph numbers that should be reproduced.
Prioritize the court's own holding and reasoning. Distinguish party arguments and quoted authorities from the court's
own position. Do not select a paragraph outside the candidate's numbered range. Account for every candidate even when
several candidates overlap or are irrelevant. Base all decisions solely on the supplied judgment passages.
"""
