import logging

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..guardrails import validate_abstract
from ..prompts import get_prompt_module
from ..runner import run_with_retry
from ..utils import generate_system_prompt
from .models import (
    AbstractOutput,
    ColIssueOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
    StepResult,
    ThemeClassificationOutput,
)

logger = logging.getLogger(__name__)


async def extract_abstract(
    text: str,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    facts_output: RelevantFactsOutput,
    pil_provisions_output: PILProvisionsOutput,
    col_issue_output: ColIssueOutput,
    court_position_output: CourtsPositionOutput,
    obiter_dicta_output: ObiterDictaOutput | None = None,
    dissenting_opinions_output: DissentingOpinionsOutput | None = None,
    previous_response_id: str | None = None,
) -> StepResult[AbstractOutput]:
    with logfire.span("abstract"):
        ABSTRACT_PROMPT = get_prompt_module(legal_system, "analysis", jurisdiction).ABSTRACT_PROMPT

        themes = ", ".join(themes_output.themes)
        facts = facts_output.relevant_facts
        pil_provisions = "\n".join(pil_provisions_output.pil_provisions)
        col_issue = col_issue_output.col_issue
        court_position = court_position_output.courts_position

        prompt_vars = {
            "text": text,
            "classification": themes,
            "facts": facts,
            "pil_provisions": pil_provisions,
            "col_issue": col_issue,
            "court_position": court_position,
        }

        if legal_system == "Common-law jurisdiction" or (jurisdiction and jurisdiction.lower() == "india"):
            obiter_dicta = obiter_dicta_output.obiter_dicta if obiter_dicta_output else ""
            dissenting_opinions = dissenting_opinions_output.dissenting_opinions if dissenting_opinions_output else ""
            prompt_vars.update({"obiter_dicta": obiter_dicta, "dissenting_opinions": dissenting_opinions})

        prompt = ABSTRACT_PROMPT.format(**prompt_vars)
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="AbstractGenerator",
            instructions=system_prompt,
            output_type=AbstractOutput,
            model=OpenAIResponsesModel(
                model=get_model("abstract"),
                openai_client=get_openai_client(),
            ),
        )
        return await run_with_retry(
            agent,
            prompt,
            AbstractOutput,
            previous_response_id=previous_response_id,
            validate=validate_abstract,
        )
