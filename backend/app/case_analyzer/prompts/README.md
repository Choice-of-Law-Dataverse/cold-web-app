# Prompt Management System

This document describes the improved prompt management system for the case analyzer.

## Overview

The prompt management system provides a centralized, organized approach to managing AI prompts used throughout the case analyzer. It includes:

- **Registry-based storage**: All prompts are registered in a central registry
- **Metadata tracking**: Each prompt has associated metadata (version, description, required parameters)
- **Automatic validation**: Prompts are validated to ensure they have required placeholders
- **Easy discovery**: List and query available prompts by legal system, jurisdiction, or type
- **Backward compatibility**: Existing code continues to work without changes

## Architecture

### Components

1. **BasePrompt**: Abstract base class for all prompts
2. **PromptMetadata**: Dataclass holding prompt metadata
3. **PromptRegistry**: Central registry for storing and retrieving prompts
4. **SimplePrompt**: Concrete implementation for string-based prompts

### Directory Structure

```
prompts/
├── __init__.py                          # Public API
├── base.py                              # Base classes and registry
├── registry.py                          # Prompt registration
├── prompt_selector.py                   # Legacy selector (unchanged)
├── prompt_selector_v2.py                # New registry-based selector
├── legal_system_type_detection.py       # Detection prompts
├── precise_jurisdiction_detection_prompt.py
├── civil_law/                           # Civil law prompts
│   ├── col_section_prompt.py
│   ├── pil_theme_prompt.py
│   └── analysis_prompts.py
├── common_law/                          # Common law prompts
│   ├── col_section_prompt.py
│   ├── pil_theme_prompt.py
│   └── analysis_prompts.py
└── india/                               # India-specific prompts
    ├── col_section_prompt.py
    ├── pil_theme_prompt.py
    └── analysis_prompts.py
```

## Usage

### For Existing Code (Backward Compatible)

The old API continues to work without any changes:

```python
from app.case_analyzer.prompts import get_prompt_module

# Get prompt module for a legal system
prompt_module = get_prompt_module(
    jurisdiction="Civil-law jurisdiction",
    prompt_type="col_section",
    specific_jurisdiction=None
)

# Access prompts as before
prompt_template = prompt_module.COL_SECTION_PROMPT
formatted = prompt_template.format(text="...")
```

### Using the New Registry API

The new API provides more features and flexibility:

```python
from app.case_analyzer.prompts import (
    get_registry,
    get_prompt_from_registry,
    get_prompt_info,
    list_available_prompts
)

# List all available prompts
prompts = list_available_prompts()
for prompt_info in prompts:
    print(f"{prompt_info['name']}: {prompt_info['description']}")

# Get a specific prompt template
template = get_prompt_from_registry(
    jurisdiction="Civil-law jurisdiction",
    prompt_type="col_section",
    specific_jurisdiction=None
)

# Get prompt metadata
info = get_prompt_info(
    legal_system="civil-law",
    jurisdiction=None,
    prompt_type="col_section"
)
print(f"Version: {info['version']}")
print(f"Required params: {info['required_params']}")

# Direct registry access
registry = get_registry()
prompt_obj = registry.get(
    legal_system="civil-law",
    jurisdiction=None,
    prompt_type="col_section"
)
formatted = prompt_obj.format(text="...")
```

## Adding New Prompts

### Option 1: Add to Existing Modules

Add your prompt to an existing module (e.g., `civil_law/analysis_prompts.py`):

```python
NEW_ANALYSIS_PROMPT = """
Your prompt text here with {parameters}.
"""
```

Then register it in `registry.py`:

```python
if hasattr(analysis_module, "NEW_ANALYSIS_PROMPT"):
    metadata = PromptMetadata(
        name=f"{legal_system}_new_analysis",
        description="Description of what this prompt does",
        version="1.0.0",
        required_params=["parameters"],
        legal_system=legal_system,
        jurisdiction=jurisdiction,
        prompt_type="new_analysis",
    )
    prompt = SimplePrompt(analysis_module.NEW_ANALYSIS_PROMPT, metadata)
    registry.register(prompt)
```

### Option 2: Create a Custom Prompt Class

For more complex prompts with custom validation or formatting:

```python
from app.case_analyzer.prompts import BasePrompt, PromptMetadata

class CustomPrompt(BasePrompt):
    def __init__(self):
        metadata = PromptMetadata(
            name="custom_analysis",
            description="Custom analysis prompt",
            version="1.0.0",
            required_params=["text", "context"],
            legal_system="civil-law",
            jurisdiction=None,
            prompt_type="custom",
        )
        super().__init__(metadata)
    
    def get_template(self) -> str:
        return """
        Custom prompt template with {text} and {context}.
        """
    
    def format(self, **kwargs):
        # Custom formatting logic
        result = super().format(**kwargs)
        # Additional processing...
        return result

# Register it
from app.case_analyzer.prompts import get_registry
registry = get_registry()
registry.register(CustomPrompt())
```

## Prompt Types

The system organizes prompts by type:

- `col_section`: Extract choice of law sections
- `theme`: Classify PIL themes
- `facts`: Extract relevant facts
- `pil_provisions`: Extract PIL provisions
- `col_issue`: Identify choice of law issues
- `courts_position`: Extract court's position
- `obiter_dicta`: Extract obiter dicta (common law)
- `dissenting_opinions`: Extract dissenting opinions (common law)
- `abstract`: Generate case abstract

## Legal Systems and Jurisdictions

The system supports:

- **Legal Systems**:
  - `civil-law`: Civil law jurisdictions
  - `common-law`: Common law jurisdictions

- **Specific Jurisdictions**:
  - `india`: India-specific prompts (inherits from common-law)
  - More can be added as needed

## Prompt Selection Logic

The registry uses a fallback mechanism to find the most specific prompt:

1. Try exact match: `legal_system` + `jurisdiction` + `prompt_type`
2. Try legal system match: `legal_system` + `prompt_type`
3. Try type-only match: `prompt_type`
4. Return `None` if no match found

## Validation

Prompts are automatically validated when registered:

- All `required_params` must appear as `{param}` placeholders in the template
- Formatting a prompt validates that all required parameters are provided
- Missing parameters raise `ValueError` with clear error messages

## Benefits

1. **Centralized Management**: All prompts in one place, easy to find and update
2. **Metadata Tracking**: Version, description, and parameters documented
3. **Automatic Validation**: Catches missing parameters early
4. **Easy Discovery**: Query prompts by legal system, jurisdiction, or type
5. **Backward Compatible**: No changes needed to existing code
6. **Extensible**: Easy to add new prompts or customize behavior
7. **Type Safe**: Clear interfaces and error messages

## Best Practices

1. **Version Your Prompts**: Increment version when making significant changes
2. **Document Parameters**: Use clear parameter names in metadata
3. **Test New Prompts**: Ensure required parameters are present in template
4. **Keep It Simple**: Use `SimplePrompt` for most cases, custom classes only when needed
5. **Follow Conventions**: Use consistent naming for prompt types and legal systems

## Migration Guide

For teams wanting to fully migrate to the new system:

1. **Phase 1**: Use backward-compatible API (no changes needed)
2. **Phase 2**: Start using new functions like `list_available_prompts()`
3. **Phase 3**: Gradually replace `get_prompt_module()` with `get_prompt_from_registry()`
4. **Phase 4**: Add custom prompt classes for advanced use cases

The system is designed to support incremental migration, so you can adopt new features at your own pace.

## Examples

### Example 1: List All Prompts for a Legal System

```python
from app.case_analyzer.prompts import get_registry

registry = get_registry()
civil_law_prompts = registry.list_by_legal_system("civil-law")

for prompt in civil_law_prompts:
    info = prompt.get_info()
    print(f"{info['name']} (v{info['version']}): {info['description']}")
```

### Example 2: Validate a Prompt Before Using

```python
from app.case_analyzer.prompts import get_prompt_info

info = get_prompt_info("civil-law", None, "abstract")
if info:
    print(f"Required parameters: {info['required_params']}")
    # Ensure you have all required parameters before formatting
```

### Example 3: Format a Prompt with Validation

```python
from app.case_analyzer.prompts import get_registry

registry = get_registry()
prompt = registry.get("civil-law", None, "col_section")

try:
    formatted = prompt.format(text="Court decision text...")
    # Use formatted prompt
except ValueError as e:
    print(f"Missing parameters: {e}")
```

## Troubleshooting

**Q: I get "Prompt not found" error**
A: Check that the prompt is registered in `registry.py` and the legal_system/jurisdiction/type match exactly.

**Q: I get "Missing required parameters" error**
A: Check the prompt's `required_params` in metadata and ensure you provide all of them.

**Q: My custom prompt doesn't appear in the registry**
A: Make sure you call `registry.register(your_prompt)` after creating it.

**Q: How do I see all registered prompts?**
A: Use `list_available_prompts()` to get a list of all prompts with their metadata.
