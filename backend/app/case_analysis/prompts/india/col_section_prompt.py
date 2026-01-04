COL_SECTION_PROMPT = """
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
-	Both ratio decidendi and obiter dicta related to choice of law
-	Jurisdiction discussions ONLY when they directly involve choice of law analysis (e.g., determining which law governs the interpretation of jurisdiction clauses, or how choice of law affects jurisdictional determinations)
-	Supporting citations and precedents only when the court explicitly relies on them for its choice of law determination
1.2 Exclude all of the following:
-	Pure procedural matters unrelated to choice of law
-	Pure jurisdictional analysis that doesn't engage with PIL choice of law principles
-	Enforcement issues not touching on choice of law
-	Other matters on the merit of the dispute unrelated to choice of law or PIL
-	Lengthy quotes from cited cases unless the court explicitly adopts them as part of its analysis

2.	Extraction Method:
-	Reproduce the court's exact language using quotation marks, abbreviating text using brackets [...] when necessary
-	Extract complete sentences with essential context only
-	Focus primarily on the court's own reasoning and analysis
3.	Output Format:
[Section 1:]
"[Exact court language]"
[Section 2:]
"[Exact court language]"
4.	Quality Check:
-	Ensure each extracted section shows the court's reasoning chain
-	Break longer passages into separate sections if they address different choice of law issues
-	If necessary, add brackets […] to abbreviate the text if it touches upon matters included in the exclusion list.
5.	CONSTRAINT: Base extraction solely on the provided judgment text. Do not add interpretive commentary or external legal knowledge.”
\nHere is the text of the Court Decision:\n{text}\n\nHere is the section of the Court Decision containing Choice of Law related information:\n
"""
