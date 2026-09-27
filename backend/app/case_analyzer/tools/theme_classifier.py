import logging
from typing import cast, get_args

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


async def jev_theme_probabilities(col_section: str) -> tuple[str, dict[Theme, float]] | None:
    """Jev's yes-probability for every theme, with the answering model; None when Jev is unavailable."""
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
    probabilities: dict[Theme, float] = {}
    for theme in themes:
        answer = response.answers.get(theme)
        if not isinstance(answer, NoulAnswer):
            return None
        probabilities[theme] = answer.noul
    return response.model, probabilities


async def _classify_with_jev(col_section: str) -> StepResult[ThemeClassificationOutput] | None:
    """Use Jev's themes only when every theme is decisive and at least one applies.

    An all-negative result falls back to the agent, which must navigate the decision before returning 'NA'.
    """
    result = await jev_theme_probabilities(col_section)
    if result is None:
        return None
    model, probabilities = result
    decisiveness = min(max(p, 1 - p) for p in probabilities.values())
    selected = cast(list[ThemeWithNA], [theme for theme, p in probabilities.items() if p >= 0.5])
    if decisiveness < JEV_MIN_CONFIDENCE or not selected:
        return None
    output = ThemeClassificationOutput(
        themes=selected,
        confidence=confidence_level(decisiveness),
        reasoning=f"Classified by {model}: "
        + ", ".join(f"{theme} ({p:.2f})" for theme, p in probabilities.items() if p >= 0.5),
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
