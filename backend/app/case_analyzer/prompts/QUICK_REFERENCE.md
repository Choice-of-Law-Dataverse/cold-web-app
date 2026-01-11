# Prompt Management System - Quick Reference

## Quick Start

### Using Existing Prompts (Backward Compatible)

```python
from app.case_analyzer.prompts import get_prompt_module

# Get prompt module
module = get_prompt_module(
    jurisdiction="Civil-law jurisdiction",
    prompt_type="col_section",
    specific_jurisdiction=None
)

# Use the prompt
template = module.COL_SECTION_PROMPT
formatted = template.format(text="Court decision text...")
```

### Using New Registry API

```python
from app.case_analyzer.prompts import get_registry

# Get registry
registry = get_registry()

# Get a prompt
prompt = registry.get(
    legal_system="civil-law",
    jurisdiction=None,
    prompt_type="col_section"
)

# Use with automatic validation
formatted = prompt.format(text="Court decision text...")
```

## Common Operations

### List All Prompts

```python
from app.case_analyzer.prompts import list_available_prompts

prompts = list_available_prompts()
for p in prompts:
    print(f"{p['name']}: {p['description']}")
```

### Get Prompt Info

```python
from app.case_analyzer.prompts import get_prompt_info

info = get_prompt_info("civil-law", None, "col_section")
print(f"Version: {info['version']}")
print(f"Parameters: {info['required_params']}")
```

### Query by Legal System

```python
registry = get_registry()
civil_law = registry.list_by_legal_system("civil-law")
print(f"Found {len(civil_law)} civil law prompts")
```

### Query by Jurisdiction

```python
registry = get_registry()
india_prompts = registry.list_by_jurisdiction("india")
print(f"Found {len(india_prompts)} India-specific prompts")
```

## CLI Tools

### List Prompts
```bash
python -m app.case_analyzer.prompts.utils list
```

### Show Prompt Info
```bash
python -m app.case_analyzer.prompts.utils info civil-law_col_section
```

### Validate All Prompts
```bash
python -m app.case_analyzer.prompts.utils validate
```

### Show Statistics
```bash
python -m app.case_analyzer.prompts.utils stats
```

## Available Prompt Types

- `col_section` - Extract choice of law sections
- `theme` - Classify PIL themes
- `facts` - Extract relevant facts
- `pil_provisions` - Extract PIL provisions
- `col_issue` - Identify choice of law issues
- `courts_position` - Extract court's position
- `obiter_dicta` - Extract obiter dicta (common law)
- `dissenting_opinions` - Extract dissenting opinions (common law)
- `abstract` - Generate case abstract

## Legal Systems

- `civil-law` - Civil law jurisdictions
- `common-law` - Common law jurisdictions

## Jurisdictions

- `india` - India-specific prompts (inherits from common-law)
- More can be added as needed

## Key Benefits

✅ **Backward Compatible** - Existing code works without changes
✅ **Type Safe** - Clear error messages for missing parameters
✅ **Versioned** - Track prompt versions over time
✅ **Validated** - Automatic validation of parameters
✅ **Discoverable** - Easy to find and query prompts
✅ **Documented** - Rich metadata for each prompt
✅ **Extensible** - Easy to add new prompts

## Migration Path

1. **Now**: Keep using `get_prompt_module()` - works as before
2. **Soon**: Use new helper functions like `list_available_prompts()`
3. **Later**: Migrate to direct registry access for better features
4. **Future**: Create custom prompt classes for advanced needs

## Error Handling

```python
from app.case_analyzer.prompts import get_registry

registry = get_registry()
prompt = registry.get("civil-law", None, "col_section")

if not prompt:
    print("Prompt not found!")
    # Handle error
else:
    try:
        formatted = prompt.format(text="...")
    except ValueError as e:
        print(f"Missing parameters: {e}")
```

## Testing

```python
# Test that prompts are registered
from app.case_analyzer.prompts import list_available_prompts

prompts = list_available_prompts()
assert len(prompts) > 0

# Test specific prompt
from app.case_analyzer.prompts import get_registry

registry = get_registry()
prompt = registry.get("civil-law", None, "col_section")
assert prompt is not None

# Test formatting
formatted = prompt.format(text="test")
assert "test" in formatted
```

## Best Practices

1. ✅ Use `list_available_prompts()` to discover what's available
2. ✅ Check `required_params` before formatting
3. ✅ Handle `ValueError` when formatting with missing params
4. ✅ Use the CLI tools to validate prompts during development
5. ✅ Document new prompts with clear descriptions
6. ✅ Version prompts when making significant changes

## Common Patterns

### Pattern 1: Get Prompt with Fallback
```python
registry = get_registry()

# Try India-specific first
prompt = registry.get("common-law", "india", "col_section")
if not prompt:
    # Fallback to general common-law
    prompt = registry.get("common-law", None, "col_section")
```

### Pattern 2: Format with Error Handling
```python
registry = get_registry()
prompt = registry.get("civil-law", None, "facts")

try:
    formatted = prompt.format(text=text, col_section=col_section)
except ValueError as e:
    logger.error(f"Failed to format prompt: {e}")
    # Handle error
```

### Pattern 3: Check Available Parameters
```python
info = prompt.get_info()
print(f"This prompt needs: {info['required_params']}")

# Ensure you have all parameters
params = {"text": text, "col_section": col_section}
missing = set(info['required_params']) - set(params.keys())
if missing:
    raise ValueError(f"Missing: {missing}")
```

## Troubleshooting

**Q: "Prompt not found" error**
- Check legal system spelling: `"civil-law"` not `"civil_law"`
- Check jurisdiction spelling: `"india"` not `"India"`
- Use CLI to list available prompts

**Q: "Missing required parameters" error**
- Check `required_params` in prompt info
- Ensure all parameters are provided to `format()`

**Q: Changes to prompts not reflected**
- Restart Python process to reload registry
- Check that prompts are registered in `registry.py`

## Resources

- Full documentation: `README.md`
- Example script: `examples.py`
- CLI utilities: `utils.py`
- Tests: `/tests/test_prompt_management.py`
