# tools/jurisdiction_detector.py
"""
Detects the jurisdiction type of a court decision: Civil-law, Common-law, or No court decision using an LLM.
"""

import asyncio
import logging

import logfire
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.case_analysis.config import get_model, get_openai_client
from app.case_analysis.prompts.legal_system_type_detection import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT

logger = logging.getLogger(__name__)


def get_jurisdiction_legal_system_mapping():
    """
    Load jurisdiction to legal system mapping from jurisdictions.csv.
    Returns a dictionary mapping jurisdiction names to legal system types.
    """
    mapping = {}

    # Known civil law jurisdictions based on jurisdictions.csv analysis
    civil_law_jurisdictions = {
        "Switzerland",
        "Germany",
        "France",
        "Italy",
        "Spain",
        "Austria",
        "Netherlands",
        "Belgium",
        "Luxembourg",
        "Portugal",
        "Greece",
        "Finland",
        "Sweden",
        "Denmark",
        "Norway",
        "Poland",
        "Czech Republic",
        "Slovakia",
        "Hungary",
        "Romania",
        "Bulgaria",
        "Croatia",
        "Slovenia",
        "Estonia",
        "Latvia",
        "Lithuania",
        "Malta",
        "Cyprus",
        "Japan",
        "South Korea",
        "China (Mainland)",
        "Taiwan",
        "Brazil",
        "Argentina",
        "Mexico",
        "Chile",
        "Colombia",
        "Peru",
        "Ecuador",
        "Bolivia",
        "Paraguay",
        "Uruguay",
        "Venezuela",
        "Russia",
        "Ukraine",
        "Turkey",
        "Egypt",
        "Morocco",
        "Tunisia",
        "Algeria",
        "Iran",
        "Lebanon",
        "Jordan",
        "Qatar",
        "Kuwait",
        "Bahrain",
        "UAE",
        "Saudi Arabia",
        "Israel",
        "Indonesia",
        "Thailand",
        "Vietnam",
        "Cambodia",
        "Laos",
        "Ethiopia",
        "Angola",
        "Mozambique",
        "Kazakhstan",
        "Uzbekistan",
        "Tajikistan",
        "Kyrgyzstan",
        "Belarus",
        "Moldova",
        "Georgia",
        "Armenia",
        "Azerbaijan",
        "Albania",
        "Bosnia and Herzegovina",
        "North Macedonia",
        "Montenegro",
        "Serbia",
        "Kosovo",
        "Iceland",
        "Liechtenstein",
        "Monaco",
        "San Marino",
        "Andorra",
        "European Union",
        "OHADA",
    }

    # Known common law jurisdictions
    common_law_jurisdictions = {
        "United States",
        "United States of America",
        "USA",
        "United Kingdom",
        "England",
        "Scotland",
        "Wales",
        "Northern Ireland",
        "Ireland",
        "Canada",
        "Australia",
        "New Zealand",
        "India",
        "Pakistan",
        "Bangladesh",
        "Sri Lanka",
        "Malaysia",
        "Singapore",
        "Hong Kong",
        "South Africa",
        "Nigeria",
        "Ghana",
        "Kenya",
        "Uganda",
        "Tanzania",
        "Zambia",
        "Zimbabwe",
        "Botswana",
        "Malawi",
        "Sierra Leone",
        "Gambia",
        "Jamaica",
        "Barbados",
        "Trinidad and Tobago",
        "Bahamas",
        "Belize",
        "Guyana",
        "Cyprus (Common Law aspects)",
        "Malta (Common Law aspects)",
        "Israel (Common Law aspects)",
        "Philippines",
        "Myanmar",
    }

    # Create the mapping
    for jurisdiction in civil_law_jurisdictions:
        mapping[jurisdiction.lower()] = "Civil-law jurisdiction"

    for jurisdiction in common_law_jurisdictions:
        mapping[jurisdiction.lower()] = "Common-law jurisdiction"

    return mapping


def detect_legal_system_by_jurisdiction(jurisdiction_name: str) -> str | None:
    """
    Detect legal system type based on jurisdiction name alone.
    Returns 'Civil-law jurisdiction', 'Common-law jurisdiction', or None if unknown.
    """
    if not jurisdiction_name or jurisdiction_name.lower() in ["unknown", "n/a", "none"]:
        return None

    mapping = get_jurisdiction_legal_system_mapping()

    # Direct lookup
    if jurisdiction_name.lower() in mapping:
        return mapping[jurisdiction_name.lower()]

    # Partial match lookup for compound names
    for mapped_jurisdiction, legal_system in mapping.items():
        if mapped_jurisdiction in jurisdiction_name.lower() or jurisdiction_name.lower() in mapped_jurisdiction:
            return legal_system

    return None


def detect_legal_system_type(jurisdiction_name: str, text: str) -> str:
    """
    Uses jurisdiction mapping first, then LLM analysis to classify the input text as:
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

        prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
        logger.debug("Using LLM analysis for jurisdiction: %s", jurisdiction_name)
        logger.debug("Prompting LLM with: %s", prompt)

        system_prompt = "You are an expert in legal systems and court decisions."

        agent = Agent(
            name="LegalSystemDetector",
            instructions=system_prompt,
            model=OpenAIChatCompletionsModel(
                model=get_model("legal_system"),
                openai_client=get_openai_client(),
            ),
        )

        result_obj = asyncio.run(Runner.run(agent, prompt))
        result = result_obj.final_output.strip()

        allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
        for option in allowed:
            if option.lower() in result.lower():
                logfire.info("Legal system detected from LLM", jurisdiction=jurisdiction_name, result=option)
                return option
        return "No court decision"
