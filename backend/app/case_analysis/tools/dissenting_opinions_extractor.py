import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analysis.config import get_model, get_openai_client
from app.case_analysis.models.analysis_models import ColIssueOutput, ColSectionOutput, DissentingOpinionsOutput
from app.case_analysis.models.classification_models import ThemeClassificationOutput
from app.case_analysis.prompts.prompt_selector import get_prompt_module
from app.case_analysis.utils.system_prompt_generator import generate_system_prompt

logger = logging.getLogger(__name__)


async def extract_dissenting_opinions(
    text: str,
    col_section_output: ColSectionOutput,
    legal_system: str,
    jurisdiction: str | None,
    themes_output: ThemeClassificationOutput,
    col_issue_output: ColIssueOutput,
) -> DissentingOpinionsOutput:
    """Extract dissenting or minority opinions for supported jurisdictions."""
    with logfire.span("dissenting_opinions"):
        prompt_module = get_prompt_module(legal_system, "analysis", jurisdiction)
        prompt_template = prompt_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT

        themes = ", ".join(themes_output.themes)
        col_issue = col_issue_output.col_issue

        prompt = prompt_template.format(
            text=text,
            col_section=str(col_section_output),
            classification=themes,
            col_issue=col_issue,
        )
        system_prompt = generate_system_prompt(legal_system, jurisdiction, "analysis")

        agent = Agent(
            name="DissentingOpinionsExtractor",
            instructions=system_prompt,
            output_type=DissentingOpinionsOutput,
            model=OpenAIChatCompletionsModel(
                model=get_model("dissenting_opinions"),
                openai_client=get_openai_client(),
            ),
        )
        run_result = await Runner.run(agent, prompt)
        return run_result.final_output_as(DissentingOpinionsOutput)
