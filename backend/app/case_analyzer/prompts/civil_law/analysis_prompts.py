# ===== RELEVANT FACTS =====
FACTS_PROMPT = """
TASK: Extract and synthesize factual elements essential for understanding the choice of law analysis into a single, coherent paragraph.
INSTRUCTIONS:
1.	Output Requirement:
Provide an answer as concise as possible, up to 300 words containing all relevant facts in narrative form.
2.	Content Priority:
Elaborate on facts including, but not limited to the following, as long as they are relevant for the private international law (PIL) and choice of law discussion in the decision:
-	Party characteristics (nationality, domicile, place of business/incorporation)
-	Nature and geography of the underlying transaction/relationship
-	Express or implied choice of law indicators
-	Specific circumstances that created the choice of law issue
3.	Writing Guidelines:
-	Use flowing, connected sentences rather than listing facts in points
-	Employ transitional phrases to link different factual elements
-	Maintain chronological or logical progression
-	Keep sentences concise but substantive
4.	Inclusion Standards:
-	Include: Connecting factors, transactional geography, choice of law clauses, foreign law invocations, conflict triggers
-	Exclude: Specific amounts, exact dates, individual names, procedural details, unrelated contract terms
5.	CONSTRAINT:
Base the factual narrative solely on the provided judgment text, synthesizing information from both the full text and extracted choice of law section.


<court_decision>
{text}
</court_decision>

<col_section>
{col_section}
</col_section>
"""

# ===== PIL PROVISIONS =====
PIL_PROVISIONS_PROMPT = """
Your task is to extract rules related to choice of law cited in a court decision. Your response is a list of provisions sorted by the impact of the rules for the choice of law issue(s) present within the court decision. Your response consists of this list only, no explanations or other additional information. A relevant provision usually stems from the most prominent legislation dealing with private international law in the respective jurisdiction. In some countries, the relevant provisions are included in the civil code. Other countries have acts that include private international law provisions. In many cases, the relevant provisions can also be found in international treaties. If no legislative provision is found, double-check whether there is any other court decision cited as a choice of law precedent.
LIMITATIONS:
- If you do not find PIL provisions in the court decision or if you are not sure, use "NA". If any language other than English is used to cite a provision, use their English abbreviation.
- No literature or other doctrinal remarks
- Do not use the paragraph symbol (§). If necessary use the abbreviation "Para."


<court_decision>
{text}
</court_decision>

<col_section>
{col_section}
</col_section>
"""

# ===== CHOICE OF LAW ISSUE =====
COL_ISSUE_PROMPT = """
Your task is to identify the main private international law issue from a court decision. Your response will be a concise question. Examples:
-	“Can the parties validly choose the law of a country with no connection to their contract?”
-	"Can an implied choice of law be inferred from forum selection clauses?"
-	"Does the closest connection test apply when parties made no express choice of law?"

The issue you extract will have to do with choice of law and the output has to be phrased in a general fashion. The issue is not about the specific details of the case but rather the overall choice-of-law issue behind the case. If any legal provisions are mentioned, use their English abbreviation.

<themes>
{classification_definitions}
</themes>

<court_decision>
{text}
</court_decision>

<col_section>
{col_section}
</col_section>
"""

# ===== COURT'S POSITION =====
COURTS_POSITION_PROMPT = """
Summarize the court's position on the choice-of-law issue(s) within the decision. Your response is phrased in a general way, generalizing the issue(s) so that your generalization could be applied to other private international law cases. If any legal provisions are mentioned, use their English abbreviation. Your output is a direct answer to the following issue:

<col_issue>
{col_issue}
</col_issue>

CONSTRAINTS:
- Base the response on the provided judgment text and extracted sections only.
- Maintain a neutral and objective tone.
- Use a maximum of 300 words.

<court_decision>
{text}
</court_decision>

<col_section>
{col_section}
</col_section>

<themes>
{classification}
</themes>
"""

# ===== ABSTRACT =====
ABSTRACT_PROMPT = """
TASK: Create a concise abstract summarizing this PIL case's choice of law analysis and outcome.
INSTRUCTIONS:
1.	Primary Approach:
Synthesize a comprehensive abstract using the analytical components you have previously extracted from this judgment.
2.	Content Integration: Your abstract must incorporate:
-	Essential facts establishing the PIL context
-	The choice of law issue(s) the court addressed
-	The court's position
3.	Structure Requirements:
-	Write exactly one paragraph
-	Begin with the factual context that created the PIL issue
-	Progress through the legal question and court's reasoning
-	Conclude with the precedential principle established
4.	Writing Standards:
-	Use clear, professional language
-	Maintain logical flow from facts to legal conclusion
-	Focus on PIL methodology and choice of law principles, not case-specific outcomes
-	Include sufficient detail for legal research purposes while remaining concise
5.  Fallback Instruction:
If an official “abstract”, “headnote”/ “case note” exists in the judgment text, extract it instead of synthesizing. Please translate it into English and state that it is a verbatim translation.

6.	CONSTRAINT: Base the abstract on your previous analysis of this judgment's PIL components, ensuring it captures the essential choice of law elements for legal research and reference purposes. Use a maximum of four sentences.


<court_decision>
{text}
</court_decision>

<themes>
{classification}
</themes>

<relevant_facts>
{facts}
</relevant_facts>

<pil_provisions>
{pil_provisions}
</pil_provisions>

<col_issue>
{col_issue}
</col_issue>

<courts_position>
{court_position}
</courts_position>
"""
