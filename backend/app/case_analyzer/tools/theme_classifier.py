import logging
from typing import get_args

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..jev import JEV_MIN_CONFIDENCE, JEV_STATE_MAX_CHARS, NoulAnswer, ask_jev, confidence_level, noul_question
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from ..utils.themes_extractor import get_themes_dict
from ..validation import validate_themes
from .document_nav import NAV_TOOLS, DocumentContext
from .models import StepResult, Theme, ThemeClassificationOutput, ThemeWithNA

logger = logging.getLogger(__name__)


async def _classify_with_jev(col_section: str) -> StepResult[ThemeClassificationOutput] | None:
    """One yes/no question per theme; None unless every theme is decisive and at least one applies.

    An all-negative result falls back to the agent, which must navigate the decision before returning 'NA'.
    """
    definitions = get_themes_dict()
    themes: tuple[Theme, ...] = get_args(Theme)
    response = await ask_jev(
        "themes",
        col_section[:JEV_STATE_MAX_CHARS],
        {
            theme: noul_question(
                f"Does the court's choice-of-law reasoning address the private international law theme '{theme}'?",
                true=definitions.get(theme),
            )
            for theme in themes
        },
    )
    if response is None:
        return None
    probabilities: dict[str, float] = {}
    for theme in themes:
        answer = response.answers.get(theme)
        if not isinstance(answer, NoulAnswer):
            return None
        probabilities[theme] = answer.noul
    decisiveness = min(max(p, 1 - p) for p in probabilities.values())
    selected: list[ThemeWithNA] = [theme for theme in themes if probabilities[theme] >= 0.5]
    if decisiveness < JEV_MIN_CONFIDENCE or not selected:
        return None
    output = ThemeClassificationOutput(
        themes=selected,
        confidence=confidence_level(decisiveness),
        reasoning=f"Classified by {response.model}: "
        + ", ".join(f"{theme} ({probabilities[theme]:.2f})" for theme in selected),
    )
    return StepResult(output=output, evidence={"jev_probabilities": probabilities})


async def classify_themes(
    doc_ctx: DocumentContext,
    col_section: str,
    legal_system: str,
    jurisdiction: str | None,
) -> StepResult[ThemeClassificationOutput]:
    with logfire.span("themes"):
        jev_result = await _classify_with_jev(col_section)
        if jev_result is not None:
            return jev_result

        PIL_THEME_PROMPT = get_prompt_module(legal_system, "theme", jurisdiction).PIL_THEME_PROMPT

        prompt = PIL_THEME_PROMPT.format(col_section=col_section, themes_table=THEMES_TABLE_STR)
        system_prompt = generate_system_prompt(legal_system, jurisdiction)

        try:
            agent = Agent[DocumentContext](
                name="ThemeClassifier",
                instructions=system_prompt,
                output_type=ThemeClassificationOutput,
                tools=NAV_TOOLS,
                model=OpenAIResponsesModel(
                    model=get_model("themes"),
                    openai_client=get_openai_client(),
                ),
            )
            return await run_agent(
                agent,
                input=prompt,
                context=doc_ctx,
                validate=validate_themes,
            )
        except Exception as e:
            logger.error("Error during theme classification: %s", e)
            raise
