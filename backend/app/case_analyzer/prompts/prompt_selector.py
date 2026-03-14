import importlib
from types import ModuleType

PROMPT_MODULES: dict[str, dict[str, str]] = {
    "civil-law": {
        "col_section": "app.case_analyzer.prompts.civil_law.col_section_prompt",
        "theme": "app.case_analyzer.prompts.civil_law.pil_theme_prompt",
        "analysis": "app.case_analyzer.prompts.civil_law.analysis_prompts",
    },
    "common-law": {
        "col_section": "app.case_analyzer.prompts.common_law.col_section_prompt",
        "theme": "app.case_analyzer.prompts.common_law.pil_theme_prompt",
        "analysis": "app.case_analyzer.prompts.common_law.analysis_prompts",
    },
    "india": {
        "col_section": "app.case_analyzer.prompts.india.col_section_prompt",
        "theme": "app.case_analyzer.prompts.india.pil_theme_prompt",
        "analysis": "app.case_analyzer.prompts.india.analysis_prompts",
    },
}

JURISDICTION_MAP: dict[str, str] = {
    "Civil-law jurisdiction": "civil-law",
    "Common-law jurisdiction": "common-law",
}


def get_prompt_module(
    jurisdiction: str | None,
    prompt_type: str,
    specific_jurisdiction: str | None = None,
) -> ModuleType:
    """Get the appropriate prompt module based on jurisdiction and legal system."""
    if specific_jurisdiction and specific_jurisdiction.lower() == "india":
        if "india" in PROMPT_MODULES and prompt_type in PROMPT_MODULES["india"]:
            module_path = PROMPT_MODULES["india"][prompt_type]
            return importlib.import_module(module_path)

    key = JURISDICTION_MAP.get(jurisdiction or "", "civil-law")
    module_path = PROMPT_MODULES[key][prompt_type]
    return importlib.import_module(module_path)
