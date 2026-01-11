# Prompt Organization

This document explains how prompts are organized in the case analyzer.

## Directory Structure

```
prompts/
├── __init__.py                          # Exports prompt access functions
├── prompt_selector.py                   # Main entry point for getting prompts
├── legal_system_type_detection.py       # Legal system detection prompt
├── precise_jurisdiction_detection_prompt.py  # Jurisdiction detection prompt
├── civil_law/                           # Civil law jurisdiction prompts
│   ├── col_section_prompt.py           # Choice of law section extraction
│   ├── pil_theme_prompt.py             # PIL theme classification
│   └── analysis_prompts.py             # Analysis prompts (facts, provisions, issues, etc.)
├── common_law/                          # Common law jurisdiction prompts
│   ├── col_section_prompt.py
│   ├── pil_theme_prompt.py
│   └── analysis_prompts.py
└── india/                               # India-specific prompts
    ├── col_section_prompt.py
    ├── pil_theme_prompt.py
    └── analysis_prompts.py
```

## Usage

Use `get_prompt_module()` to access jurisdiction-specific prompts:

```python
from app.case_analyzer.prompts import get_prompt_module

# Get civil law prompts
module = get_prompt_module(
    jurisdiction="Civil-law jurisdiction",
    prompt_type="col_section",
    specific_jurisdiction=None
)
prompt = module.COL_SECTION_PROMPT.format(text="...")

# Get India-specific prompts
module = get_prompt_module(
    jurisdiction="Common-law jurisdiction",
    prompt_type="analysis",
    specific_jurisdiction="India"
)
prompt = module.FACTS_PROMPT.format(text="...", col_section="...")
```

## Prompt Types

### col_section
Extracts choice of law sections from court decisions.
- Available in: `civil_law/`, `common_law/`, `india/`
- Constant: `COL_SECTION_PROMPT`

### theme
Classifies PIL themes in court decisions.
- Available in: `civil_law/`, `common_law/`, `india/`
- Constant: `PIL_THEME_PROMPT`

### analysis
Contains multiple analysis prompts:
- `FACTS_PROMPT` - Extract relevant facts
- `PIL_PROVISIONS_PROMPT` - Extract PIL provisions
- `COL_ISSUE_PROMPT` - Identify choice of law issues
- `COURTS_POSITION_PROMPT` - Extract court's position
- `COURTS_POSITION_OBITER_DICTA_PROMPT` - Extract obiter dicta (common law only)
- `COURTS_POSITION_DISSENTING_OPINIONS_PROMPT` - Extract dissenting opinions (common law only)
- `ABSTRACT_PROMPT` - Generate case abstract

## How Prompt Selection Works

The `get_prompt_module()` function uses a fallback strategy:

1. **Check for jurisdiction-specific prompts**: If `specific_jurisdiction="India"`, looks for India-specific prompts first
2. **Fallback to legal system prompts**: Uses civil-law or common-law prompts based on jurisdiction
3. **Dynamic import**: Imports the appropriate module at runtime

Example:
```python
# For India, tries: india/analysis_prompts.py
# Falls back to: common_law/analysis_prompts.py
get_prompt_module("Common-law jurisdiction", "analysis", "India")
```

## Adding New Prompts

### 1. Add prompt to existing module
Edit the appropriate file (e.g., `civil_law/analysis_prompts.py`):
```python
NEW_PROMPT = """
Your prompt text with {parameters}.
"""
```

### 2. Add new jurisdiction
Create a new directory following the pattern:
```
new_jurisdiction/
├── col_section_prompt.py
├── pil_theme_prompt.py
└── analysis_prompts.py
```

Update `prompt_selector.py`:
```python
PROMPT_MODULES = {
    "new-jurisdiction": {
        "col_section": "app.case_analyzer.prompts.new_jurisdiction.col_section_prompt",
        "theme": "app.case_analyzer.prompts.new_jurisdiction.pil_theme_prompt",
        "analysis": "app.case_analyzer.prompts.new_jurisdiction.analysis_prompts",
    },
}
```

## Design Principles

- **Simple**: Direct imports, no complex abstractions
- **Organized**: Prompts grouped by legal system and jurisdiction
- **Flexible**: Easy to add new jurisdictions or prompt types
- **No overhead**: Prompts are plain strings, loaded only when needed
