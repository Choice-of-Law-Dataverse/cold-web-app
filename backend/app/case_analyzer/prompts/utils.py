"""Utility script to inspect and manage prompts.

This script provides command-line tools for working with the prompt registry.

Usage:
    python -m app.case_analyzer.prompts.utils list              # List all prompts
    python -m app.case_analyzer.prompts.utils info <name>       # Get prompt info
    python -m app.case_analyzer.prompts.utils validate          # Validate all prompts
    python -m app.case_analyzer.prompts.utils stats             # Show statistics
"""

import sys
from typing import Any

from .base import get_registry


def list_prompts(filter_by: str | None = None) -> None:
    """List all prompts in the registry."""
    registry = get_registry()
    prompts = registry.list_all()

    if filter_by:
        # Filter by legal_system, jurisdiction, or prompt_type
        filter_key, filter_value = filter_by.split("=")
        prompts = [
            p
            for p in prompts
            if getattr(p.metadata, filter_key, None) == filter_value
        ]

    print(f"\n{'='*80}")
    print(f"Registered Prompts ({len(prompts)} total)")
    print(f"{'='*80}\n")

    for prompt in sorted(prompts, key=lambda p: p.metadata.name):
        info = prompt.get_info()
        print(f"Name:         {info['name']}")
        print(f"Description:  {info['description']}")
        print(f"Version:      {info['version']}")
        print(f"Type:         {info['prompt_type']}")
        print(f"Legal Sys:    {info['legal_system'] or 'N/A'}")
        print(f"Jurisdiction: {info['jurisdiction'] or 'N/A'}")
        print(f"Parameters:   {', '.join(info['required_params'])}")
        print(f"{'-'*80}")


def show_prompt_info(name: str) -> None:
    """Show detailed information about a specific prompt."""
    registry = get_registry()
    prompts = registry.list_all()

    prompt = next((p for p in prompts if p.metadata.name == name), None)

    if not prompt:
        print(f"Error: Prompt '{name}' not found")
        return

    info = prompt.get_info()
    template = prompt.get_template()

    print(f"\n{'='*80}")
    print(f"Prompt: {info['name']}")
    print(f"{'='*80}\n")

    print(f"Description:  {info['description']}")
    print(f"Version:      {info['version']}")
    print(f"Type:         {info['prompt_type']}")
    print(f"Legal System: {info['legal_system'] or 'N/A'}")
    print(f"Jurisdiction: {info['jurisdiction'] or 'N/A'}")
    print(f"Parameters:   {', '.join(info['required_params'])}")

    print(f"\n{'-'*80}")
    print("Template Preview:")
    print(f"{'-'*80}\n")

    # Show first 500 characters of template
    preview = template[:500]
    if len(template) > 500:
        preview += "..."
    print(preview)


def validate_prompts() -> None:
    """Validate all prompts in the registry."""
    registry = get_registry()
    prompts = registry.list_all()

    print(f"\n{'='*80}")
    print("Validating Prompts")
    print(f"{'='*80}\n")

    errors = []

    for prompt in prompts:
        try:
            # Validation happens in __init__, so if it exists it's valid
            # But we can do additional checks
            info = prompt.get_info()
            template = prompt.get_template()

            # Check that template is not empty
            if not template.strip():
                errors.append(f"{info['name']}: Template is empty")

            # Check that template contains required parameters
            for param in info["required_params"]:
                if f"{{{param}}}" not in template:
                    errors.append(
                        f"{info['name']}: Missing parameter placeholder '{param}'"
                    )

        except Exception as e:
            errors.append(f"{prompt.metadata.name}: {e}")

    if errors:
        print("❌ Validation failed with the following errors:\n")
        for error in errors:
            print(f"  - {error}")
        print()
    else:
        print(f"✅ All {len(prompts)} prompts validated successfully!\n")


def show_stats() -> None:
    """Show statistics about registered prompts."""
    registry = get_registry()
    prompts = registry.list_all()

    # Count by legal system
    by_legal_system: dict[str, int] = {}
    by_jurisdiction: dict[str, int] = {}
    by_type: dict[str, int] = {}

    for prompt in prompts:
        info = prompt.get_info()

        legal_sys = info["legal_system"] or "None"
        by_legal_system[legal_sys] = by_legal_system.get(legal_sys, 0) + 1

        jurisdiction = info["jurisdiction"] or "None"
        by_jurisdiction[jurisdiction] = by_jurisdiction.get(jurisdiction, 0) + 1

        prompt_type = info["prompt_type"] or "None"
        by_type[prompt_type] = by_type.get(prompt_type, 0) + 1

    print(f"\n{'='*80}")
    print("Prompt Statistics")
    print(f"{'='*80}\n")

    print(f"Total Prompts: {len(prompts)}")

    print(f"\nBy Legal System:")
    for legal_sys, count in sorted(by_legal_system.items()):
        print(f"  {legal_sys:20s}: {count:3d}")

    print(f"\nBy Jurisdiction:")
    for jurisdiction, count in sorted(by_jurisdiction.items()):
        print(f"  {jurisdiction:20s}: {count:3d}")

    print(f"\nBy Type:")
    for prompt_type, count in sorted(by_type.items()):
        print(f"  {prompt_type:20s}: {count:3d}")

    print()


def main() -> None:
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        filter_by = sys.argv[2] if len(sys.argv) > 2 else None
        list_prompts(filter_by)
    elif command == "info":
        if len(sys.argv) < 3:
            print("Error: Please provide a prompt name")
            sys.exit(1)
        show_prompt_info(sys.argv[2])
    elif command == "validate":
        validate_prompts()
    elif command == "stats":
        show_stats()
    else:
        print(f"Error: Unknown command '{command}'")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
