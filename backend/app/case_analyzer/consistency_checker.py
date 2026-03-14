"""Cross-step consistency validation for case analysis outputs."""

import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from .config import get_openai_client
from .tools.models import (
    ColIssueOutput,
    ConsistencyCheckOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)

CONSISTENCY_PROMPT = """Review these analysis outputs from a court decision for internal consistency.

Themes: {themes}
Relevant Facts: {facts}
PIL Provisions: {provisions}
Choice of Law Issue: {col_issue}
Court's Position: {position}
{extra_sections}
Check for:
1. Do the themes match what is described in the COL issue?
2. Are the relevant facts actually relevant to the COL issue?
3. Do the PIL provisions relate to the identified themes and COL issue?
4. Does the court's position address the identified COL issue?
5. Is there contradictory information between any steps?

Only flag genuine inconsistencies. If the outputs are coherent, mark as consistent with no issues.
Flag as "high" severity only when a step clearly contradicts another or is completely irrelevant to the rest."""


async def check_consistency(
    themes_output: ThemeClassificationOutput,
    facts_output: RelevantFactsOutput,
    provisions_output: PILProvisionsOutput,
    col_issue_output: ColIssueOutput,
    position_output: CourtsPositionOutput,
    obiter_output: ObiterDictaOutput | None = None,
    dissent_output: DissentingOpinionsOutput | None = None,
    previous_response_id: str | None = None,
) -> ConsistencyCheckOutput:
    with logfire.span("consistency_check"):
        extra_sections = ""
        if obiter_output:
            extra_sections += f"Obiter Dicta: {obiter_output.obiter_dicta}\n"
        if dissent_output:
            extra_sections += f"Dissenting Opinions: {dissent_output.dissenting_opinions}\n"

        prompt = CONSISTENCY_PROMPT.format(
            themes=", ".join(themes_output.themes),
            facts=facts_output.relevant_facts,
            provisions="\n".join(provisions_output.pil_provisions),
            col_issue=col_issue_output.col_issue,
            position=position_output.courts_position,
            extra_sections=extra_sections,
        )

        agent = Agent(
            name="ConsistencyChecker",
            instructions="You are a quality assurance reviewer for legal case analysis. Be precise and only flag genuine inconsistencies between analysis steps.",
            output_type=ConsistencyCheckOutput,
            model=OpenAIResponsesModel(
                model="gpt-5-nano",
                openai_client=get_openai_client(),
            ),
        )

        try:
            run_result = await Runner.run(agent, prompt, previous_response_id=previous_response_id)
            result = run_result.final_output_as(ConsistencyCheckOutput)
            if not result.is_consistent:
                for issue in result.issues:
                    logger.warning("Consistency issue [%s] in %s: %s", issue.severity, issue.step, issue.description)
            return result
        except Exception as e:
            logger.error("Consistency check failed: %s", e)
            return ConsistencyCheckOutput(is_consistent=True, issues=[])
