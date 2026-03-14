"""Jurisdiction-specific system prompt generator with optional summaries from jurisdictions.csv."""

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_jurisdiction_summaries() -> dict[str, str]:
    """Load jurisdiction summaries from jurisdictions.csv."""
    try:
        current_dir = Path(__file__).parent.parent
        csv_path = current_dir / "data" / "jurisdictions.csv"

        if not csv_path.exists():
            logger.warning("jurisdictions.csv not found at %s", csv_path)
            return {}

        jurisdiction_summaries = {}

        with open(csv_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = str(row.get("Name", "")).strip()
                summary = str(row.get("Jurisdiction Summary", "")).strip()

                if name and name.lower() != "nan" and summary and summary.lower() != "nan":
                    jurisdiction_summaries[name] = summary

        return jurisdiction_summaries

    except Exception as e:
        logger.error("Error loading jurisdiction summaries: %s", e)
        return {}


def generate_base_system_prompt() -> str:
    """Generate the base system prompt with general instructions for legal analysis."""
    return """You are an expert in private international law and choice of law analysis.

CORE INSTRUCTIONS:
- Be precise and analytical in your responses
- Base all analysis STRICTLY on the information provided in the court decision text
- Do not infer, assume, or add information not explicitly stated in the source material
- Focus specifically on private international law and choice of law elements
- Provide clear, legally sound reasoning for your conclusions

OUTPUT LANGUAGE:
- Always provide your final output in English, even when the court decision text is in another language
- EXCEPTION: When exact quotes are required for legal analysis, preserve the original language
- When translating legal concepts, use established English legal terminology

ANALYSIS STANDARDS:
- Identify only the private international law elements that are explicitly discussed in the decision
- Extract factual elements that are relevant to the choice of law analysis
- Focus on connecting factors, jurisdictional elements, and conflict of laws rules
- Maintain objectivity and avoid interpretive speculation beyond what the court has stated"""


def generate_jurisdiction_specific_prompt(
    jurisdiction_name: str | None = None,
    legal_system_type: str | None = None,
) -> str:
    """Generate a system prompt with jurisdiction-specific context appended to the base prompt."""
    system_prompt = generate_base_system_prompt()

    if jurisdiction_name and jurisdiction_name != "Unknown":
        jurisdiction_summaries = load_jurisdiction_summaries()

        if jurisdiction_name in jurisdiction_summaries:
            summary = jurisdiction_summaries[jurisdiction_name]
            system_prompt += f"""

JURISDICTION-SPECIFIC CONTEXT:
This case originates from {jurisdiction_name}. The following provides relevant context about the private international law framework in this jurisdiction:

{summary}

Use this contextual information to inform your analysis, but remember to base your conclusions on what is actually stated in the court decision text."""
        else:
            system_prompt += f"""

JURISDICTION CONTEXT:
This case originates from {jurisdiction_name}. Consider this jurisdictional context when analyzing the private international law elements of the decision."""

    if legal_system_type and legal_system_type not in ["Unknown legal system", None]:
        system_prompt += f"""

LEGAL SYSTEM CONTEXT:
This decision comes from a {legal_system_type.lower().replace("jurisdiction", "legal system")}. Consider the typical approaches and methodologies of this legal tradition in your analysis."""

    return system_prompt


def generate_system_prompt(
    legal_system_type: str | None = None,
    specific_jurisdiction: str | None = None,
) -> str:
    """Generate system prompt based on legal system type and jurisdiction."""
    return generate_jurisdiction_specific_prompt(specific_jurisdiction, legal_system_type)
