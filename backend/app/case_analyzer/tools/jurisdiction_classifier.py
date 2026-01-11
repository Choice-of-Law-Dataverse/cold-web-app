# tools/precise_jurisdiction_detector.py
"""
Identifies the precise jurisdiction from court decision text using the jurisdictions.csv database.
"""

import csv
import logging
from pathlib import Path

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analyzer.config import get_model, get_openai_client
from app.case_analyzer.models.classification_models import JurisdictionOutput
from app.case_analyzer.prompts.precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT

from .jurisdiction_detector import (
    detect_legal_system_by_jurisdiction,
    detect_legal_system_type,
)

logger = logging.getLogger(__name__)


async def determine_legal_system_type(jurisdiction_name: str, text: str | None = None) -> str:
    if text is not None:
        return await detect_legal_system_type(jurisdiction_name, text)
    fallback = detect_legal_system_by_jurisdiction(jurisdiction_name)
    return fallback or "No court decision"


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


def create_jurisdiction_list():
    """Create a formatted list of jurisdictions for the LLM prompt."""
    jurisdictions = load_jurisdictions()
    jurisdiction_list = []

    for jurisdiction in jurisdictions:
        jurisdiction_list.append(f"- {jurisdiction['name']}")

    return "\n".join(jurisdiction_list)


async def detect_precise_jurisdiction_with_confidence(text: str) -> JurisdictionOutput:
    """
    Uses an LLM to identify the precise jurisdiction from court decision text with confidence.
    Returns a JurisdictionOutput Pydantic model with jurisdiction data including confidence and reasoning.
    """
    with logfire.span("jurisdiction_classification"):
        if not text or len(text.strip()) < 50:
            return JurisdictionOutput(
                precise_jurisdiction="Unknown",
                legal_system_type="Unknown",
                jurisdiction_code="UNK",
                confidence="low",
                reasoning="Text too short for analysis",
            )

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
                model=OpenAIChatCompletionsModel(
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
