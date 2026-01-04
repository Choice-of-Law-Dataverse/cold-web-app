# utils/system_prompt_generator.py
"""
Dynamic system prompt generator that creates jurisdiction-specific system prompts
with optional jurisdiction summaries from jurisdictions.csv
"""
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_jurisdiction_summaries():
    """
    Load jurisdiction summaries from jurisdictions.csv

    Returns:
        dict: Dictionary mapping jurisdiction names to their summaries
    """
    try:
        # Get the path to jurisdictions.csv
        current_dir = Path(__file__).parent.parent  # streamlit directory
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


def generate_base_system_prompt():
    """
    Generate the base system prompt with general instructions for legal analysis.

    Returns:
        str: Base system prompt
    """
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


def generate_jurisdiction_specific_prompt(jurisdiction_name=None, legal_system_type=None):
    """
    Generate a dynamic system prompt based on jurisdiction and legal system.

    Args:
        jurisdiction_name (str, optional): Specific jurisdiction name (e.g., "Germany", "United States")
        legal_system_type (str, optional): Legal system type (e.g., "Civil-law jurisdiction", "Common-law jurisdiction")

    Returns:
        str: Complete system prompt with jurisdiction-specific context
    """
    # Start with base prompt
    system_prompt = generate_base_system_prompt()

    # Add jurisdiction-specific context if available
    if jurisdiction_name and jurisdiction_name != "Unknown":
        # Load jurisdiction summaries
        jurisdiction_summaries = load_jurisdiction_summaries()

        if jurisdiction_name in jurisdiction_summaries:
            summary = jurisdiction_summaries[jurisdiction_name]
            system_prompt += f"""

JURISDICTION-SPECIFIC CONTEXT:
This case originates from {jurisdiction_name}. The following provides relevant context about the private international law framework in this jurisdiction:

{summary}

Use this contextual information to inform your analysis, but remember to base your conclusions on what is actually stated in the court decision text."""
        else:
            # Even if no summary is available, mention the jurisdiction
            system_prompt += f"""

JURISDICTION CONTEXT:
This case originates from {jurisdiction_name}. Consider this jurisdictional context when analyzing the private international law elements of the decision."""

    # Add legal system type context if available
    if legal_system_type and legal_system_type not in ["Unknown legal system", None]:
        system_prompt += f"""

LEGAL SYSTEM CONTEXT:
This decision comes from a {legal_system_type.lower().replace('jurisdiction', 'legal system')}. Consider the typical approaches and methodologies of this legal tradition in your analysis."""

    return system_prompt


def get_system_prompt_for_analysis(state):
    """
    Generate system prompt based on the current analysis state.

    Args:
        state (dict): Current analysis state containing jurisdiction information

    Returns:
        str: Appropriate system prompt for the current analysis
    """
    # Extract jurisdiction information from state
    jurisdiction_name = None
    legal_system_type = None

    # Check different possible keys in state for jurisdiction info
    if "precise_jurisdiction" in state:
        jurisdiction_name = state["precise_jurisdiction"]
    elif "jurisdiction_name" in state:
        jurisdiction_name = state["jurisdiction_name"]

    if "jurisdiction" in state:
        legal_system_type = state["jurisdiction"]
    elif "legal_system_type" in state:
        legal_system_type = state["legal_system_type"]

    # Generate the appropriate prompt
    return generate_jurisdiction_specific_prompt(jurisdiction_name, legal_system_type)


def generate_system_prompt(legal_system_type, specific_jurisdiction, phase):
    """
    Generate system prompt based on explicit parameters.

    Args:
        legal_system_type (str): Legal system type (e.g., "Civil-law jurisdiction")
        specific_jurisdiction (str): Specific jurisdiction (e.g., "Switzerland")
        phase (str): Analysis phase (e.g., "col_section", "theme", "analysis")

    Returns:
        str: Appropriate system prompt for the analysis
    """
    return generate_jurisdiction_specific_prompt(specific_jurisdiction, legal_system_type)


# Convenience function for backward compatibility
def get_default_system_prompt():
    """
    Get the default system prompt (base prompt without jurisdiction specifics).

    Returns:
        str: Default system prompt
    """
    return generate_base_system_prompt()
