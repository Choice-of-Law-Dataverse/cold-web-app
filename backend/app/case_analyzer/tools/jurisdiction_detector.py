# tools/jurisdiction_detector.py
"""
Detects the jurisdiction type of a court decision: Civil-law, Common-law, or No court decision using an LLM.
"""

import csv
import logging
from functools import cache
from pathlib import Path

import logfire
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel

from ..config import get_model, get_openai_client
from ..jev import JEV_STATE_MAX_CHARS, ask_jev, choice_question, confident_choice
from ..prompts import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT

logger = logging.getLogger(__name__)

_JURISDICTIONS_CSV = Path(__file__).parent.parent / "data" / "jurisdictions.csv"
_FAMILY_LEGAL_SYSTEMS = {"Civil Law": "Civil-law jurisdiction", "Common Law": "Common-law jurisdiction"}

LEGAL_SYSTEM_CRITERIA: dict[str, str] = {
    "Civil-law jurisdiction": (
        "Legal systems based on comprehensive written codes (Romano-Germanic tradition): "
        "the court applies codified statutes and articles rather than binding precedent."
    ),
    "Common-law jurisdiction": (
        "Legal systems based on judicial precedent and case law (Anglo-American tradition): "
        "the court reasons from prior decisions under stare decisis."
    ),
    "No court decision": "The text is not a judicial decision or cannot be classified.",
}


@cache
def _legal_families() -> dict[str, str]:
    """CoLD's curated legal family by jurisdiction name (casefolded), from jurisdictions.csv."""
    with open(_JURISDICTIONS_CSV, encoding="utf-8") as f:
        return {row["Name"].strip().casefold(): row["Legal Family"].strip() for row in csv.DictReader(f) if row["Name"].strip()}


def legal_system_from_family(family: str) -> str | None:
    """The legal system a curated family names, or None when it names both traditions or neither.

    Roman-Dutch, religious, supranational and mixed civil/common-law families are left to the text:
    South Africa and Indonesia are both Roman-Dutch, yet one decides like a common-law court and the other does not.
    """
    traditions = {part.strip() for part in family.split(",")} & set(_FAMILY_LEGAL_SYSTEMS)
    return _FAMILY_LEGAL_SYSTEMS[traditions.pop()] if len(traditions) == 1 else None


def detect_legal_system_by_jurisdiction(jurisdiction_name: str) -> str | None:
    """
    Legal system from the jurisdiction's curated legal family alone.
    Returns 'Civil-law jurisdiction', 'Common-law jurisdiction', or None when the family does not decide it.
    """
    if not jurisdiction_name:
        return None
    return legal_system_from_family(_legal_families().get(jurisdiction_name.strip().casefold(), ""))


async def detect_legal_system_type(jurisdiction_name: str, text: str) -> str:
    """
    Uses the jurisdiction's curated legal family first, then Jev, then LLM analysis to classify the input text as:
    - 'Civil-law jurisdiction'
    - 'Common-law jurisdiction'
    - 'No court decision'
    """
    with logfire.span("legal_system", jurisdiction=jurisdiction_name):
        if not text or len(text.strip()) < 50:
            return "No court decision"

        jurisdiction_based_result = detect_legal_system_by_jurisdiction(jurisdiction_name)
        if jurisdiction_based_result:
            logger.debug("Jurisdiction-based classification: %s -> %s", jurisdiction_name, jurisdiction_based_result)
            logfire.info("Legal system detected from mapping", jurisdiction=jurisdiction_name, result=jurisdiction_based_result)
            return jurisdiction_based_result

        response = await ask_jev(
            "legal_system",
            {"jurisdiction": jurisdiction_name, "text": text[:JEV_STATE_MAX_CHARS]},
            {
                "legal_system": choice_question(
                    "Which legal tradition does this court decision come from? The stated jurisdiction is highly reliable.",
                    LEGAL_SYSTEM_CRITERIA,
                )
            },
        )
        answer = confident_choice(response, "legal_system") if response else None
        if answer:
            logfire.info("Legal system detected from Jev", jurisdiction=jurisdiction_name, result=answer.choice)
            return answer.choice

        prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
        logger.debug("Using LLM analysis for jurisdiction: %s", jurisdiction_name)
        logger.debug("Prompting LLM with: %s", prompt)

        system_prompt = "You are an expert in legal systems and court decisions."

        agent = Agent(
            name="LegalSystemDetector",
            instructions=system_prompt,
            model=OpenAIResponsesModel(
                model=get_model("legal_system"),
                openai_client=get_openai_client(),
            ),
        )

        result_obj = await Runner.run(agent, prompt)
        result = result_obj.final_output.strip()

        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        for option in allowed:
            if option.lower() in result.lower():
                logfire.info("Legal system detected from LLM", jurisdiction=jurisdiction_name, result=option)
                return option
        return "No court decision"
