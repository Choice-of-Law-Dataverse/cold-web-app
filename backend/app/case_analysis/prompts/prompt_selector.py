import importlib

PROMPT_MODULES = {
    "civil-law": {
        "col_section": "app.case_analysis.prompts.civil_law.col_section_prompt",
        "theme": "app.case_analysis.prompts.civil_law.pil_theme_prompt",
        "analysis": "app.case_analysis.prompts.civil_law.analysis_prompts",
    },
    "common-law": {
        "col_section": "app.case_analysis.prompts.common_law.col_section_prompt",
        "theme": "app.case_analysis.prompts.common_law.pil_theme_prompt",
        "analysis": "app.case_analysis.prompts.common_law.analysis_prompts",
    },
    "india": {
        "col_section": "app.case_analysis.prompts.india.col_section_prompt",
        "theme": "app.case_analysis.prompts.india.pil_theme_prompt",
        "analysis": "app.case_analysis.prompts.india.analysis_prompts",
    },
}

# Map user-facing jurisdiction to key
JURISDICTION_MAP = {
    "Civil-law jurisdiction": "civil-law",
    "Common-law jurisdiction": "common-law",
}

def get_prompt_module(jurisdiction, prompt_type, specific_jurisdiction=None):
    """
    Get the appropriate prompt module based on jurisdiction and specific jurisdiction.

    Args:
        jurisdiction: The legal system type (e.g., 'Civil-law jurisdiction', 'Common-law jurisdiction')
        prompt_type: The type of prompt needed ('col_section', 'theme', 'analysis')
        specific_jurisdiction: The specific jurisdiction name (e.g., 'India')

    Returns:
        The imported prompt module
    """
    # Check if we have specific prompts for this jurisdiction
    if specific_jurisdiction and specific_jurisdiction.lower() == "india":
        if "india" in PROMPT_MODULES and prompt_type in PROMPT_MODULES["india"]:
            module_path = PROMPT_MODULES["india"][prompt_type]
            return importlib.import_module(module_path)

    # Fall back to general legal system prompts
    key = JURISDICTION_MAP.get(jurisdiction, "civil-law")
    module_path = PROMPT_MODULES[key][prompt_type]
    return importlib.import_module(module_path)

# Usage:
# get_prompt_module(jurisdiction, 'col_section').COL_SECTION_PROMPT
# get_prompt_module(jurisdiction, 'theme').PIL_THEME_PROMPT
# get_prompt_module(jurisdiction, 'analysis').ABSTRACT_PROMPT
#
# For specific jurisdictions:
# get_prompt_module(jurisdiction, 'col_section', specific_jurisdiction='India').COL_SECTION_PROMPT
