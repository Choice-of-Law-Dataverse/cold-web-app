# tools/precise_jurisdiction_detector.py
"""
Identifies the precise jurisdiction from court decision text using the jurisdictions.csv database.
"""

import csv
import logging
from functools import cache
from pathlib import Path

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..jev import (
    JEV_MIN_CONFIDENCE,
    JEV_STATE_MAX_CHARS,
    ChoiceAnswer,
    ask_jev,
    choice_question,
    confidence_level,
    jev_reasoning,
)
from ..prompts import PRECISE_JURISDICTION_DETECTION_PROMPT
from .jurisdiction_detector import detect_legal_system_type
from .models import JurisdictionOutput

logger = logging.getLogger(__name__)


def load_jurisdictions():
    """Load all jurisdictions from the CSV file."""
    jurisdictions_file = Path(__file__).parent.parent / "data" / "jurisdictions.csv"
    jurisdictions = []

    with open(jurisdictions_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"].strip():  # Only include rows with actual jurisdiction names
                jurisdictions.append(
                    {
                        "name": row["Name"].strip(),
                        "code": row["Alpha-3 Code"].strip(),
                        "summary": row["Jurisdiction Summary"].strip(),
                    }
                )
    # Sort jurisdictions by name for better consistency
    jurisdictions.sort(key=lambda x: x["name"].lower())
    return jurisdictions


def create_jurisdiction_list() -> str:
    """Format jurisdictions as a newline-delimited string for LLM prompts."""
    jurisdictions = load_jurisdictions()
    jurisdiction_list = []

    for jurisdiction in jurisdictions:
        jurisdiction_list.append(f"- {jurisdiction['name']}")

    return "\n".join(jurisdiction_list)


@cache
def jurisdiction_codes() -> dict[str, str]:
    """Alpha-3 code by jurisdiction name, from jurisdictions.csv."""
    return {j["name"]: j["code"] for j in load_jurisdictions()}


async def jev_jurisdiction(text: str) -> tuple[str, ChoiceAnswer] | None:
    """Jev's jurisdiction answer, with the answering model; None when Jev is unavailable."""
    response = await ask_jev(
        "jurisdiction_classification",
        text[:JEV_STATE_MAX_CHARS],
        {
            "jurisdiction": choice_question(
                "In which jurisdiction was this court decision issued? Use court names, cited statutes, "
                "geographic references, language and citation format.",
                dict.fromkeys(jurisdiction_codes()),
            ),
        },
    )
    answer = response.answers.get("jurisdiction") if response else None
    if response is None or not isinstance(answer, ChoiceAnswer):
        return None
    return response.model, answer


async def _detect_with_jev(text: str) -> JurisdictionOutput | None:
    """Classify the jurisdiction with Jev; None when not confident. The legal system is set by the caller."""
    result = await jev_jurisdiction(text)
    if result is None:
        return None
    model, jurisdiction = result
    codes = jurisdiction_codes()
    if jurisdiction.confidence < JEV_MIN_CONFIDENCE or jurisdiction.choice not in codes:
        return None
    return JurisdictionOutput(
        precise_jurisdiction=jurisdiction.choice,
        legal_system_type="Unknown",
        jurisdiction_code=codes[jurisdiction.choice],
        confidence=confidence_level(jurisdiction.confidence),
        reasoning=jev_reasoning(model, f"{jurisdiction.choice} ({jurisdiction.confidence:.2f})"),
    )


async def detect_precise_jurisdiction_with_confidence(text: str) -> JurisdictionOutput:
    """
    Identifies the precise jurisdiction (Jev first, then an LLM agent), then its legal system with
    detect_legal_system_type: the curated legal family first, then Jev, then the jurisdiction agent's own answer,
    then an LLM agent.
    """
    with logfire.span("jurisdiction_classification"):
        result = await _detect_jurisdiction(text)
        if result.precise_jurisdiction == "Unknown":
            return result
        try:
            legal_system = await detect_legal_system_type(result.precise_jurisdiction, text, fallback=result.legal_system_type)
        except Exception as e:
            logger.error("Error in legal system detection: %s", e)
            return result
        return result.model_copy(update={"legal_system_type": legal_system})


async def _detect_jurisdiction(text: str) -> JurisdictionOutput:
    if not text or len(text.strip()) < 50:
        return JurisdictionOutput(
            precise_jurisdiction="Unknown",
            legal_system_type="Unknown",
            jurisdiction_code="UNK",
            confidence="low",
            reasoning="Text too short for analysis",
        )

    jev_result = await _detect_with_jev(text)
    if jev_result is not None:
        return jev_result

    jurisdiction_list = create_jurisdiction_list()

    prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
        jurisdiction_list=jurisdiction_list,
        text=text[:5000],
    )
    logger.debug("Prompting agent with structured output for jurisdiction detection")

    try:
        system_prompt = "You are an expert in legal systems and court jurisdictions worldwide. Analyze the court decision and identify the precise jurisdiction, legal system type, and provide your confidence level and reasoning."

        agent = Agent(
            name="JurisdictionDetector",
            instructions=system_prompt,
            output_type=JurisdictionOutput,
            model=OpenAIResponsesModel(
                model=get_model("jurisdiction_classification"),
                openai_client=get_openai_client(),
            ),
        )

        run_result = await Runner.run(agent, prompt)
        result = run_result.final_output_as(JurisdictionOutput)

        jurisdiction_name = result.precise_jurisdiction
        legal_system_type = result.legal_system_type
        jurisdiction_code = result.jurisdiction_code
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Detected jurisdiction: %s (%s) with confidence %s", jurisdiction_name, legal_system_type, confidence)

        # Validate against known jurisdictions
        jurisdictions = load_jurisdictions()

        if jurisdiction_name and jurisdiction_name != "Unknown":
            for jurisdiction in jurisdictions:
                if jurisdiction["name"].lower() == jurisdiction_name.lower():
                    return JurisdictionOutput(
                        precise_jurisdiction=jurisdiction["name"],
                        legal_system_type=legal_system_type,
                        jurisdiction_code=jurisdiction["code"],
                        confidence=confidence,
                        reasoning=reasoning,
                    )

            for jurisdiction in jurisdictions:
                if (
                    jurisdiction_name.lower() in jurisdiction["name"].lower()
                    or jurisdiction["name"].lower() in jurisdiction_name.lower()
                ):
                    return JurisdictionOutput(
                        precise_jurisdiction=jurisdiction["name"],
                        legal_system_type=legal_system_type,
                        jurisdiction_code=jurisdiction["code"],
                        confidence=confidence,
                        reasoning=reasoning + " (partial match)",
                    )

            if len(jurisdiction_name) > 2 and jurisdiction_name not in ["Unknown", "unknown", "N/A", "None"]:
                return JurisdictionOutput(
                    precise_jurisdiction=jurisdiction_name,
                    legal_system_type=legal_system_type,
                    jurisdiction_code=jurisdiction_code if jurisdiction_code != "UNK" else "N/A",
                    confidence=confidence,
                    reasoning=reasoning + " (not in standard jurisdiction list)",
                )

        return JurisdictionOutput(
            precise_jurisdiction="Unknown",
            legal_system_type="Unknown",
            jurisdiction_code="UNK",
            confidence="low",
            reasoning="Could not identify jurisdiction from the text",
        )

    except Exception as e:
        logger.error("Error in jurisdiction detection: %s", e)
        return JurisdictionOutput(
            precise_jurisdiction="Unknown",
            legal_system_type="Unknown",
            jurisdiction_code="UNK",
            confidence="low",
            reasoning=f"Error during detection: {str(e)}",
        )
