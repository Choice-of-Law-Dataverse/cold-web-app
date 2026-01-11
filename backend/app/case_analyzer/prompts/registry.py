"""Prompt registry initialization and configuration."""

import logging

from .base import BasePrompt, PromptMetadata, get_registry

logger = logging.getLogger(__name__)


class SimplePrompt(BasePrompt):
    """A simple prompt implementation that wraps a template string."""

    def __init__(self, template: str, metadata: PromptMetadata):
        self._template = template
        super().__init__(metadata)

    def get_template(self) -> str:
        return self._template


def register_all_prompts() -> None:
    """Register all prompts in the global registry."""
    registry = get_registry()

    # Import existing prompt modules to register them
    from . import civil_law, common_law, india

    # Register civil law prompts
    _register_legal_system_prompts(registry, "civil-law", civil_law)

    # Register common law prompts
    _register_legal_system_prompts(registry, "common-law", common_law)

    # Register India-specific prompts
    _register_legal_system_prompts(registry, "common-law", india, jurisdiction="india")

    logger.info("Registered %d prompts in the registry", len(registry.list_all()))


def _register_legal_system_prompts(
    registry, legal_system: str, module, jurisdiction: str | None = None
) -> None:
    """Helper to register prompts from a module."""
    # Register col_section prompt
    if hasattr(module, "col_section_prompt"):
        col_section_module = module.col_section_prompt
        if hasattr(col_section_module, "COL_SECTION_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_col_section",
                description="Extract choice of law sections from court decisions",
                version="1.0.0",
                required_params=["text"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="col_section",
            )
            prompt = SimplePrompt(col_section_module.COL_SECTION_PROMPT, metadata)
            registry.register(prompt)

    # Register theme prompt
    if hasattr(module, "pil_theme_prompt"):
        theme_module = module.pil_theme_prompt
        if hasattr(theme_module, "PIL_THEME_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_theme",
                description="Classify PIL themes in court decisions",
                version="1.0.0",
                required_params=["themes_table", "text", "col_section"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="theme",
            )
            prompt = SimplePrompt(theme_module.PIL_THEME_PROMPT, metadata)
            registry.register(prompt)

    # Register analysis prompts
    if hasattr(module, "analysis_prompts"):
        analysis_module = module.analysis_prompts

        # Facts prompt
        if hasattr(analysis_module, "FACTS_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_facts",
                description="Extract relevant facts for PIL analysis",
                version="1.0.0",
                required_params=["text", "col_section"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="facts",
            )
            prompt = SimplePrompt(analysis_module.FACTS_PROMPT, metadata)
            registry.register(prompt)

        # PIL provisions prompt
        if hasattr(analysis_module, "PIL_PROVISIONS_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_pil_provisions",
                description="Extract PIL provisions cited in court decisions",
                version="1.0.0",
                required_params=["text", "col_section"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="pil_provisions",
            )
            prompt = SimplePrompt(analysis_module.PIL_PROVISIONS_PROMPT, metadata)
            registry.register(prompt)

        # COL issue prompt
        if hasattr(analysis_module, "COL_ISSUE_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_col_issue",
                description="Identify choice of law issues in court decisions",
                version="1.0.0",
                required_params=["classification_definitions", "text", "col_section"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="col_issue",
            )
            prompt = SimplePrompt(analysis_module.COL_ISSUE_PROMPT, metadata)
            registry.register(prompt)

        # Courts position prompt
        if hasattr(analysis_module, "COURTS_POSITION_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_courts_position",
                description="Extract court's position on choice of law issues",
                version="1.0.0",
                required_params=["col_issue", "text", "col_section", "classification"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="courts_position",
            )
            prompt = SimplePrompt(analysis_module.COURTS_POSITION_PROMPT, metadata)
            registry.register(prompt)

        # Obiter dicta prompt (Common law only)
        if hasattr(analysis_module, "COURTS_POSITION_OBITER_DICTA_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_obiter_dicta",
                description="Extract obiter dicta on choice of law issues",
                version="1.0.0",
                required_params=["col_issue", "text", "col_section", "classification"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="obiter_dicta",
            )
            prompt = SimplePrompt(
                analysis_module.COURTS_POSITION_OBITER_DICTA_PROMPT, metadata
            )
            registry.register(prompt)

        # Dissenting opinions prompt (Common law only)
        if hasattr(analysis_module, "COURTS_POSITION_DISSENTING_OPINIONS_PROMPT"):
            metadata = PromptMetadata(
                name=f"{legal_system}_dissenting_opinions",
                description="Extract dissenting opinions on choice of law issues",
                version="1.0.0",
                required_params=["col_issue", "text", "col_section", "classification"],
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="dissenting_opinions",
            )
            prompt = SimplePrompt(
                analysis_module.COURTS_POSITION_DISSENTING_OPINIONS_PROMPT, metadata
            )
            registry.register(prompt)

        # Abstract prompt
        if hasattr(analysis_module, "ABSTRACT_PROMPT"):
            # Determine required params based on legal system
            base_params = [
                "text",
                "classification",
                "facts",
                "pil_provisions",
                "col_issue",
                "court_position",
            ]
            if legal_system == "common-law" or jurisdiction == "india":
                base_params.extend(["obiter_dicta", "dissenting_opinions"])

            metadata = PromptMetadata(
                name=f"{legal_system}_abstract",
                description="Generate abstract for PIL case analysis",
                version="1.0.0",
                required_params=base_params,
                legal_system=legal_system,
                jurisdiction=jurisdiction,
                prompt_type="abstract",
            )
            prompt = SimplePrompt(analysis_module.ABSTRACT_PROMPT, metadata)
            registry.register(prompt)


# Initialize prompts on module import
try:
    register_all_prompts()
except Exception as e:
    logger.error("Failed to register prompts: %s", e)
