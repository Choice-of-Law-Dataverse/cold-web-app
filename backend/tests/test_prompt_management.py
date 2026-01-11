"""Tests for the prompt management system."""

import pytest

from app.case_analyzer.prompts.base import (
    BasePrompt,
    PromptMetadata,
    PromptRegistry,
)


class TestPrompt(BasePrompt):
    """Test prompt implementation."""

    def __init__(self, template: str, metadata: PromptMetadata):
        self._template = template
        super().__init__(metadata)

    def get_template(self) -> str:
        return self._template


def test_prompt_metadata_creation():
    """Test creating prompt metadata."""
    metadata = PromptMetadata(
        name="test_prompt",
        description="A test prompt",
        version="1.0.0",
        required_params=["text", "context"],
        legal_system="civil-law",
        jurisdiction="switzerland",
        prompt_type="test",
    )

    assert metadata.name == "test_prompt"
    assert metadata.version == "1.0.0"
    assert len(metadata.required_params) == 2


def test_prompt_validation_success():
    """Test that valid prompts pass validation."""
    metadata = PromptMetadata(
        name="valid_prompt",
        description="Valid test prompt",
        version="1.0.0",
        required_params=["text", "context"],
    )

    template = "This is a prompt with {text} and {context}."
    prompt = TestPrompt(template, metadata)

    assert prompt.get_template() == template


def test_prompt_validation_failure():
    """Test that invalid prompts fail validation."""
    metadata = PromptMetadata(
        name="invalid_prompt",
        description="Invalid test prompt",
        version="1.0.0",
        required_params=["text", "context", "missing"],
    )

    template = "This prompt has {text} and {context} but is missing a parameter."

    with pytest.raises(ValueError) as exc_info:
        TestPrompt(template, metadata)

    assert "missing required parameters" in str(exc_info.value).lower()
    assert "missing" in str(exc_info.value)


def test_prompt_format_success():
    """Test formatting a prompt with all required parameters."""
    metadata = PromptMetadata(
        name="format_prompt",
        description="Format test prompt",
        version="1.0.0",
        required_params=["text", "context"],
    )

    template = "Text: {text}, Context: {context}"
    prompt = TestPrompt(template, metadata)

    formatted = prompt.format(text="Hello", context="World")
    assert formatted == "Text: Hello, Context: World"


def test_prompt_format_missing_param():
    """Test formatting fails when required parameters are missing."""
    metadata = PromptMetadata(
        name="format_prompt",
        description="Format test prompt",
        version="1.0.0",
        required_params=["text", "context"],
    )

    template = "Text: {text}, Context: {context}"
    prompt = TestPrompt(template, metadata)

    with pytest.raises(ValueError) as exc_info:
        prompt.format(text="Hello")  # Missing 'context'

    assert "missing required parameters" in str(exc_info.value).lower()


def test_prompt_get_info():
    """Test getting prompt information."""
    metadata = PromptMetadata(
        name="info_prompt",
        description="Info test prompt",
        version="1.0.0",
        required_params=["text"],
        legal_system="civil-law",
        jurisdiction="switzerland",
        prompt_type="test",
    )

    template = "Test {text}"
    prompt = TestPrompt(template, metadata)

    info = prompt.get_info()

    assert info["name"] == "info_prompt"
    assert info["version"] == "1.0.0"
    assert info["legal_system"] == "civil-law"
    assert info["jurisdiction"] == "switzerland"
    assert info["prompt_type"] == "test"


def test_registry_register_and_get():
    """Test registering and retrieving prompts from registry."""
    registry = PromptRegistry()

    metadata = PromptMetadata(
        name="test_registry_prompt",
        description="Registry test prompt",
        version="1.0.0",
        required_params=["text"],
        legal_system="civil-law",
        jurisdiction=None,
        prompt_type="test",
    )

    template = "Test {text}"
    prompt = TestPrompt(template, metadata)

    registry.register(prompt)

    retrieved = registry.get(legal_system="civil-law", prompt_type="test")
    assert retrieved is not None
    assert retrieved.metadata.name == "test_registry_prompt"


def test_registry_fallback():
    """Test registry fallback mechanism."""
    registry = PromptRegistry()

    # Register a general prompt
    metadata_general = PromptMetadata(
        name="general_prompt",
        description="General prompt",
        version="1.0.0",
        required_params=["text"],
        legal_system="civil-law",
        jurisdiction=None,
        prompt_type="test",
    )
    prompt_general = TestPrompt("General {text}", metadata_general)
    registry.register(prompt_general)

    # Register a specific prompt for Switzerland
    metadata_specific = PromptMetadata(
        name="switzerland_prompt",
        description="Switzerland-specific prompt",
        version="1.0.0",
        required_params=["text"],
        legal_system="civil-law",
        jurisdiction="switzerland",
        prompt_type="test",
    )
    prompt_specific = TestPrompt("Swiss {text}", metadata_specific)
    registry.register(prompt_specific)

    # Should get specific prompt when jurisdiction is specified
    retrieved_specific = registry.get(
        legal_system="civil-law", jurisdiction="switzerland", prompt_type="test"
    )
    assert retrieved_specific.metadata.name == "switzerland_prompt"

    # Should get general prompt when jurisdiction is not found
    retrieved_general = registry.get(
        legal_system="civil-law", jurisdiction="germany", prompt_type="test"
    )
    assert retrieved_general.metadata.name == "general_prompt"


def test_registry_list_by_legal_system():
    """Test listing prompts by legal system."""
    registry = PromptRegistry()

    # Register prompts for different legal systems
    for system in ["civil-law", "common-law"]:
        for i in range(3):
            metadata = PromptMetadata(
                name=f"{system}_prompt_{i}",
                description=f"Test prompt {i}",
                version="1.0.0",
                required_params=["text"],
                legal_system=system,
                prompt_type=f"type_{i}",
            )
            prompt = TestPrompt(f"Test {i} {{text}}", metadata)
            registry.register(prompt)

    civil_law_prompts = registry.list_by_legal_system("civil-law")
    assert len(civil_law_prompts) == 3

    common_law_prompts = registry.list_by_legal_system("common-law")
    assert len(common_law_prompts) == 3


def test_registry_list_by_jurisdiction():
    """Test listing prompts by jurisdiction."""
    registry = PromptRegistry()

    # Register India-specific prompts
    for i in range(2):
        metadata = PromptMetadata(
            name=f"india_prompt_{i}",
            description=f"India test prompt {i}",
            version="1.0.0",
            required_params=["text"],
            legal_system="common-law",
            jurisdiction="india",
            prompt_type=f"type_{i}",
        )
        prompt = TestPrompt(f"India test {i} {{text}}", metadata)
        registry.register(prompt)

    india_prompts = registry.list_by_jurisdiction("india")
    assert len(india_prompts) == 2


def test_registry_list_by_type():
    """Test listing prompts by type."""
    registry = PromptRegistry()

    # Register prompts of same type for different systems
    for system in ["civil-law", "common-law"]:
        metadata = PromptMetadata(
            name=f"{system}_col_section",
            description=f"{system} col section prompt",
            version="1.0.0",
            required_params=["text"],
            legal_system=system,
            prompt_type="col_section",
        )
        prompt = TestPrompt(f"{system} {{text}}", metadata)
        registry.register(prompt)

    col_section_prompts = registry.list_by_type("col_section")
    assert len(col_section_prompts) == 2


def test_registry_list_all():
    """Test listing all prompts in registry."""
    registry = PromptRegistry()

    # Register multiple prompts
    for i in range(5):
        metadata = PromptMetadata(
            name=f"prompt_{i}",
            description=f"Test prompt {i}",
            version="1.0.0",
            required_params=["text"],
            prompt_type=f"type_{i}",
        )
        prompt = TestPrompt(f"Test {i} {{text}}", metadata)
        registry.register(prompt)

    all_prompts = registry.list_all()
    assert len(all_prompts) == 5
