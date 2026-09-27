import logging
from typing import Any, cast, get_args

import logfire
from agents import Agent
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..jev import (
    JEV_MIN_CONFIDENCE,
    JEV_STATE_MAX_CHARS,
    NoulAnswer,
    ask_jev,
    confidence_level,
    jev_reasoning,
    noul_question,
)
from ..prompts import get_prompt_module
from ..runner import run_agent
from ..utils import THEMES_TABLE_STR, generate_system_prompt
from ..utils.themes_extractor import get_themes_dict
from ..validation import validate_themes
from .document_nav import NAV_TOOLS, DocumentContext
from .models import StepResult, Theme, ThemeClassificationOutput, ThemeWithNA

logger = logging.getLogger(__name__)


THEME_PARENTS: dict[Theme, Theme] = {
    "Partial choice": "Freedom of Choice",
    "Dépeçage": "Freedom of Choice",
    "Freedom of Choice": "Party autonomy",
    "Tacit choice": "Party autonomy",
    "Rules of Law": "Party autonomy",
}
"""CoLD's theme hierarchy: a decision tagged with a theme is also tagged with its parent. Children come
before their parents, so one pass propagates probabilities up the tree."""

DERIVED_THEMES: frozenset[Theme] = frozenset({"Party autonomy"})
"""Themes CoLD never tags on their own, so Jev is not asked about them; they follow from their children."""

JEV_THEME_CRITERIA: dict[Theme, tuple[dict[str, Any], dict[str, Any]]] = {
    "Freedom of Choice": (
        {
            "what": "The court examines an express choice of law by the parties: whether they could choose, "
            "what they chose, or the validity, scope or limits of that choice.",
            "examples": ["Is the choice-of-law clause valid?", "May the parties choose a law unconnected to the contract?"],
        },
        {"what": "No express choice is examined: the choice is only implied, absent, or merely mentioned."},
    ),
    "Tacit choice": (
        {
            "what": "The court asks whether the parties chose a law implicitly, inferring it from contract terms, "
            "a choice-of-court or arbitration clause, references to a law, or their conduct in the proceedings.",
            "examples": ["Does a choice of court imply a choice of law?"],
        },
        {"what": "No implied choice is at issue: the choice is express, or none is argued."},
    ),
    "Partial choice": (
        {"what": "The parties' choice of law covers only part of the contract."},
        {"what": "Any choice covers the whole contract."},
    ),
    "Dépeçage": (
        {"what": "Different laws govern different issues or parts of the same contract or legal relationship."},
        {"what": "One law governs every issue."},
    ),
    "Absence of choice": (
        {
            "what": "The court determines the applicable law objectively because the parties made no valid choice, "
            "using connecting factors such as closest connection, characteristic performance or place of contracting.",
        },
        {"what": "The court applies a law the parties chose, expressly or tacitly."},
    ),
    "Rules of Law": (
        {
            "what": "Non-State law is chosen or applied as the governing rules: UNIDROIT Principles, lex mercatoria, "
            "the CISG as chosen rules, or religious or customary law.",
        },
        {"what": "Only national law is chosen or applied."},
    ),
    "Public policy": (
        {
            "what": "The court refuses or limits applying a foreign law, judgment or award because it conflicts with "
            "the forum's fundamental principles (ordre public).",
        },
        {"what": "No public policy exception is invoked."},
    ),
    "Mandatory rules": (
        {
            "what": "Overriding mandatory rules (lois de police) of the forum or another State apply regardless of "
            "the law governing the contract.",
        },
        {"what": "No overriding mandatory rule displaces or limits the governing law."},
    ),
    "Arbitration": (
        {
            "what": "The choice-of-law question arises in or about arbitration: the law arbitrators apply, "
            "the arbitration agreement, or the enforcement of an award.",
        },
        {"what": "Arbitration is absent or mentioned only in passing."},
    ),
    "Consumer contracts": (
        {"what": "Special choice-of-law rules protecting consumers apply to the contract."},
        {"what": "The contract is not a consumer contract, or its consumer protection rules are not at issue."},
    ),
    "Employment contracts": (
        {"what": "Special choice-of-law rules protecting employees apply to the contract."},
        {"what": "The contract is not an employment contract, or its employee protection rules are not at issue."},
    ),
}


def _theme_question(theme: Theme, definition: str | None) -> dict[str, Any]:
    true, false = JEV_THEME_CRITERIA[theme]
    return noul_question(
        {
            "question": "Is this court decision classified under the private international law theme `theme`?",
            "focus": "Classify what the court's choice-of-law reasoning decides, not every concept it mentions.",
            "theme": {"name": theme, "definition": definition},
        },
        true=true,
        false=false,
    )


async def jev_theme_probabilities(col_section: str) -> tuple[str, dict[Theme, float]] | None:
    """Jev's yes-probability for every theme, with the answering model; None when Jev is unavailable.

    A parent theme's probability is the highest of its own and its children's, so selecting every
    theme at 0.5 or above always yields a set consistent with the hierarchy.
    """
    definitions = get_themes_dict()
    asked: list[Theme] = [theme for theme in get_args(Theme) if theme not in DERIVED_THEMES]
    response = await ask_jev(
        "themes",
        col_section[:JEV_STATE_MAX_CHARS],
        {theme: _theme_question(theme, definitions.get(theme)) for theme in asked},
    )
    if response is None:
        return None
    probabilities: dict[Theme, float] = dict.fromkeys(get_args(Theme), 0.0)
    for theme in asked:
        answer = response.answers.get(theme)
        if not isinstance(answer, NoulAnswer):
            return None
        probabilities[theme] = answer.noul
    for child, parent in THEME_PARENTS.items():
        probabilities[parent] = max(probabilities[parent], probabilities[child])
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
        reasoning=jev_reasoning(model, ", ".join(f"{theme} ({p:.2f})" for theme, p in probabilities.items() if p >= 0.5)),
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
