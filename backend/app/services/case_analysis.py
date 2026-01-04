"""
Case analysis service for processing court decisions.
Adapted from cold-case-analysis repository.
"""

import asyncio
import io
import logging
from collections.abc import AsyncGenerator
from typing import Any, Literal

import logfire
import pymupdf4llm
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from pydantic import BaseModel

from app.config import config

logger = logging.getLogger(__name__)

_openai_client = None


def get_openai_client():
    """
    Get singleton OpenAI client for agents.

    Note: nest_asyncio.apply() is required because the openai-agents library
    uses asyncio.run() internally, which would fail in an already-running async
    context (like FastAPI). nest_asyncio patches asyncio to allow nested event loops.
    This is applied once when the client is first created.
    """
    global _openai_client
    if _openai_client is None:
        import nest_asyncio
        import openai

        nest_asyncio.apply()
        _openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


class ColSectionOutput(BaseModel):
    """Choice of Law section extraction results."""

    col_sections: list[str]
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class JurisdictionOutput(BaseModel):
    """Jurisdiction detection results."""

    legal_system_type: str
    precise_jurisdiction: str
    jurisdiction_code: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class ThemeOutput(BaseModel):
    """Theme classification results."""

    themes: list[str]
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class AbstractOutput(BaseModel):
    """Abstract generation results."""

    abstract: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class RelevantFactsOutput(BaseModel):
    """Relevant facts extraction results."""

    relevant_facts: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class PILProvisionsOutput(BaseModel):
    """PIL provisions extraction results."""

    pil_provisions: list[str]
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class ColIssueOutput(BaseModel):
    """COL issue extraction results."""

    col_issue: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class CourtsPositionOutput(BaseModel):
    """Court's position extraction results."""

    courts_position: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


class CaseCitationOutput(BaseModel):
    """Case citation extraction results."""

    case_citation: str
    confidence: Literal["low", "medium", "high"]
    reasoning: str


def get_llm_model() -> str:
    """Get the configured LLM model name."""
    return "gpt-4o-mini"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pymupdf4llm."""
    with logfire.span("pdf_extraction"):
        try:
            pdf_stream = io.BytesIO(pdf_bytes)
            markdown_text = pymupdf4llm.to_markdown(pdf_stream)
            return markdown_text
        except Exception as e:
            error_msg = f"Failed to extract text from PDF: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e


def detect_jurisdiction(text: str) -> JurisdictionOutput:
    """
    Detect jurisdiction from court decision text.

    Note: Uses asyncio.run() internally via the agents library. This works in
    FastAPI's async context because nest_asyncio is applied in get_openai_client().
    """
    with logfire.span("jurisdiction_detection"):
        if not text or len(text.strip()) < 50:
            return JurisdictionOutput(
                legal_system_type="No court decision",
                precise_jurisdiction="Unknown",
                jurisdiction_code="XX",
                confidence="low",
                reasoning="Text too short for analysis",
            )

        prompt = f"""Analyze this court decision and identify:
1. Legal system type (Civil-law jurisdiction, Common-law jurisdiction, or No court decision)
2. Precise jurisdiction (country name)
3. ISO country code (2 or 3 letter code)

Court decision text:
{text[:2000]}

Provide your analysis with confidence level and reasoning."""

        system_prompt = "You are an expert in legal systems and jurisdiction identification."

        agent = Agent(
            name="JurisdictionDetector",
            instructions=system_prompt,
            output_type=JurisdictionOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(JurisdictionOutput)
        return result


def extract_col_section(text: str, legal_system: str, jurisdiction: str) -> ColSectionOutput:
    """Extract Choice of Law sections from court decision."""
    with logfire.span("col_extraction"):
        prompt = f"""Extract all Choice of Law sections from this court decision.
Focus on sections that discuss:
- Choice of law rules
- Applicable law determination
- Conflict of laws analysis
- Private international law considerations

Legal system: {legal_system}
Jurisdiction: {jurisdiction}

Court decision text:
{text[:3000]}

Return the extracted sections as a list."""

        system_prompt = f"You are an expert in {legal_system} and Choice of Law analysis for {jurisdiction}."

        agent = Agent(
            name="ColExtractor",
            instructions=system_prompt,
            output_type=ColSectionOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ColSectionOutput)
        return result


def classify_themes(col_sections: list[str], legal_system: str) -> ThemeOutput:
    """Classify PIL themes from COL sections."""
    with logfire.span("theme_classification"):
        valid_themes = [
            "Party autonomy",
            "Tacit choice",
            "Partial choice",
            "Absence of choice",
            "Arbitration",
            "Freedom of Choice",
            "Rules of Law",
            "Dépeçage",
            "Public policy",
            "Mandatory rules",
            "Consumer contracts",
            "Employment contracts",
        ]

        prompt = f"""Classify the PIL themes present in these Choice of Law sections.

Valid themes: {', '.join(valid_themes)}

COL Sections:
{' '.join(col_sections[:2000])}

Return applicable themes from the list above."""

        system_prompt = f"You are an expert in Private International Law themes for {legal_system}."

        agent = Agent(
            name="ThemeClassifier",
            instructions=system_prompt,
            output_type=ThemeOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ThemeOutput)
        return result


def extract_case_citation(text: str, jurisdiction: str) -> CaseCitationOutput:
    """Extract formal case citation."""
    with logfire.span("case_citation"):
        prompt = f"""Extract the formal case citation from this court decision.
Format it according to academic citation standards for {jurisdiction}.

Text:
{text[:1000]}

Return the citation in standard format."""

        agent = Agent(
            name="CitationExtractor",
            instructions="You are an expert in legal citation formats.",
            output_type=CaseCitationOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(CaseCitationOutput)
        return result


def generate_abstract(col_sections: list[str], legal_system: str) -> AbstractOutput:
    """Generate case abstract."""
    with logfire.span("abstract_generation"):
        prompt = f"""Generate a concise abstract of this court decision focusing on PIL aspects.

COL Sections:
{' '.join(col_sections[:2000])}

Provide a 2-3 sentence summary."""

        agent = Agent(
            name="AbstractGenerator",
            instructions=f"You are an expert in {legal_system} case analysis.",
            output_type=AbstractOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(AbstractOutput)
        return result


def extract_relevant_facts(text: str, legal_system: str) -> RelevantFactsOutput:
    """Extract relevant facts from court decision."""
    with logfire.span("facts_extraction"):
        prompt = f"""Extract the relevant facts from this court decision.
Focus on facts relevant to the Choice of Law analysis.

Text:
{text[:2000]}

Provide a clear summary of the relevant facts."""

        agent = Agent(
            name="FactsExtractor",
            instructions=f"You are an expert in {legal_system} case analysis.",
            output_type=RelevantFactsOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(RelevantFactsOutput)
        return result


def extract_pil_provisions(text: str, legal_system: str, jurisdiction: str) -> PILProvisionsOutput:
    """Extract PIL provisions cited in the decision."""
    with logfire.span("pil_provisions"):
        prompt = f"""Extract all Private International Law provisions cited in this court decision.
Include statute numbers, article numbers, and provision names.

Jurisdiction: {jurisdiction}

Text:
{text[:2000]}

Return as a list of provisions."""

        agent = Agent(
            name="ProvisionsExtractor",
            instructions=f"You are an expert in {legal_system} PIL provisions for {jurisdiction}.",
            output_type=PILProvisionsOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(PILProvisionsOutput)
        return result


def extract_col_issue(col_sections: list[str], legal_system: str) -> ColIssueOutput:
    """Extract the Choice of Law issue from the case."""
    with logfire.span("col_issue"):
        prompt = f"""Identify the main Choice of Law issue(s) in this case.

COL Sections:
{' '.join(col_sections[:2000])}

State the issue clearly and concisely."""

        agent = Agent(
            name="IssueExtractor",
            instructions=f"You are an expert in {legal_system} Choice of Law analysis.",
            output_type=ColIssueOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(ColIssueOutput)
        return result


def extract_courts_position(col_sections: list[str], legal_system: str) -> CourtsPositionOutput:
    """Extract the court's position and reasoning."""
    with logfire.span("courts_position"):
        prompt = f"""Extract the court's position and reasoning on the Choice of Law issue.

COL Sections:
{' '.join(col_sections[:2000])}

Provide a clear explanation of the court's analysis and conclusion."""

        agent = Agent(
            name="PositionExtractor",
            instructions=f"You are an expert in {legal_system} judicial reasoning.",
            output_type=CourtsPositionOutput,
            model=OpenAIChatCompletionsModel(
                model=get_llm_model(),
                openai_client=get_openai_client(),
            ),
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output_as(CourtsPositionOutput)
        return result


async def analyze_case_streaming(
    text: str, jurisdiction_data: dict[str, Any]
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Execute complete case analysis workflow with streaming updates.

    Yields intermediate results as they complete.
    """
    legal_system = jurisdiction_data["legal_system_type"]
    jurisdiction = jurisdiction_data["precise_jurisdiction"]

    with logfire.span("case_analysis_workflow"):
        yield {"step": "col_extraction", "status": "in_progress"}

        try:
            col_result = extract_col_section(text, legal_system, jurisdiction)
            yield {
                "step": "col_extraction",
                "status": "completed",
                "data": {
                    "col_sections": col_result.col_sections,
                    "confidence": col_result.confidence,
                    "reasoning": col_result.reasoning,
                },
            }
        except Exception as e:
            logger.error("COL extraction failed: %s", str(e))
            yield {"step": "col_extraction", "status": "error", "error": str(e)}
            return

        col_sections = col_result.col_sections

        yield {"step": "theme_classification", "status": "in_progress"}
        try:
            theme_result = classify_themes(col_sections, legal_system)
            yield {
                "step": "theme_classification",
                "status": "completed",
                "data": {
                    "themes": theme_result.themes,
                    "confidence": theme_result.confidence,
                    "reasoning": theme_result.reasoning,
                },
            }
        except Exception as e:
            logger.error("Theme classification failed: %s", str(e))
            yield {"step": "theme_classification", "status": "error", "error": str(e)}

        yield {"step": "case_citation", "status": "in_progress"}
        try:
            citation_result = extract_case_citation(text, jurisdiction)
            yield {
                "step": "case_citation",
                "status": "completed",
                "data": {
                    "case_citation": citation_result.case_citation,
                    "confidence": citation_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Case citation extraction failed: %s", str(e))
            yield {"step": "case_citation", "status": "error", "error": str(e)}

        yield {"step": "abstract", "status": "in_progress"}
        try:
            abstract_result = generate_abstract(col_sections, legal_system)
            yield {
                "step": "abstract",
                "status": "completed",
                "data": {"abstract": abstract_result.abstract, "confidence": abstract_result.confidence},
            }
        except Exception as e:
            logger.error("Abstract generation failed: %s", str(e))
            yield {"step": "abstract", "status": "error", "error": str(e)}

        yield {"step": "relevant_facts", "status": "in_progress"}
        try:
            facts_result = extract_relevant_facts(text, legal_system)
            yield {
                "step": "relevant_facts",
                "status": "completed",
                "data": {
                    "relevant_facts": facts_result.relevant_facts,
                    "confidence": facts_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Facts extraction failed: %s", str(e))
            yield {"step": "relevant_facts", "status": "error", "error": str(e)}

        yield {"step": "pil_provisions", "status": "in_progress"}
        try:
            provisions_result = extract_pil_provisions(text, legal_system, jurisdiction)
            yield {
                "step": "pil_provisions",
                "status": "completed",
                "data": {
                    "pil_provisions": provisions_result.pil_provisions,
                    "confidence": provisions_result.confidence,
                },
            }
        except Exception as e:
            logger.error("PIL provisions extraction failed: %s", str(e))
            yield {"step": "pil_provisions", "status": "error", "error": str(e)}

        yield {"step": "col_issue", "status": "in_progress"}
        try:
            issue_result = extract_col_issue(col_sections, legal_system)
            yield {
                "step": "col_issue",
                "status": "completed",
                "data": {"choice_of_law_issue": issue_result.col_issue, "confidence": issue_result.confidence},
            }
        except Exception as e:
            logger.error("COL issue extraction failed: %s", str(e))
            yield {"step": "col_issue", "status": "error", "error": str(e)}

        yield {"step": "courts_position", "status": "in_progress"}
        try:
            position_result = extract_courts_position(col_sections, legal_system)
            yield {
                "step": "courts_position",
                "status": "completed",
                "data": {
                    "courts_position": position_result.courts_position,
                    "confidence": position_result.confidence,
                },
            }
        except Exception as e:
            logger.error("Court's position extraction failed: %s", str(e))
            yield {"step": "courts_position", "status": "error", "error": str(e)}

        yield {"step": "analysis_complete", "status": "completed"}
