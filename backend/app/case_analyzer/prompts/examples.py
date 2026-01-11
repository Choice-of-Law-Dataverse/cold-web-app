"""Example script demonstrating the improved prompt management system.

This script shows how to use the new prompt registry system for managing
and accessing prompts in the case analyzer.
"""

from app.case_analyzer.prompts import (
    get_prompt_module,
    get_registry,
    list_available_prompts,
)


def example_legacy_api():
    """Example using the legacy API (backward compatible)."""
    print("\n" + "=" * 80)
    print("Example 1: Using Legacy API (Backward Compatible)")
    print("=" * 80 + "\n")

    # This works exactly as before
    prompt_module = get_prompt_module(
        jurisdiction="Civil-law jurisdiction",
        prompt_type="col_section",
        specific_jurisdiction=None,
    )

    # Access the prompt template
    template = prompt_module.COL_SECTION_PROMPT
    print("Got COL_SECTION_PROMPT template")
    print(f"Template length: {len(template)} characters")
    print(f"First 200 chars: {template[:200]}...")


def example_list_prompts():
    """Example listing all available prompts."""
    print("\n" + "=" * 80)
    print("Example 2: Listing All Available Prompts")
    print("=" * 80 + "\n")

    prompts = list_available_prompts()
    print(f"Total prompts registered: {len(prompts)}\n")

    # Show a few examples
    print("Sample prompts:")
    for prompt_info in prompts[:5]:
        print(f"\n  Name: {prompt_info['name']}")
        print(f"  Type: {prompt_info['prompt_type']}")
        print(f"  Legal System: {prompt_info['legal_system']}")
        print(f"  Description: {prompt_info['description']}")
        print(f"  Required Params: {', '.join(prompt_info['required_params'])}")


def example_direct_registry():
    """Example using the registry directly."""
    print("\n" + "=" * 80)
    print("Example 3: Using Registry Directly")
    print("=" * 80 + "\n")

    registry = get_registry()

    # Get a specific prompt
    prompt = registry.get(
        legal_system="civil-law", jurisdiction=None, prompt_type="col_section"
    )

    if prompt:
        info = prompt.get_info()
        print(f"Found prompt: {info['name']}")
        print(f"Version: {info['version']}")
        print(f"Required parameters: {', '.join(info['required_params'])}")

        # Format the prompt with parameters
        try:
            formatted = prompt.format(text="Sample court decision text")
            print(f"\n✓ Prompt formatted successfully")
            print(f"  Formatted length: {len(formatted)} characters")
        except ValueError as e:
            print(f"\n✗ Error formatting prompt: {e}")


def example_query_by_system():
    """Example querying prompts by legal system."""
    print("\n" + "=" * 80)
    print("Example 4: Query Prompts by Legal System")
    print("=" * 80 + "\n")

    registry = get_registry()

    # List all civil law prompts
    civil_law_prompts = registry.list_by_legal_system("civil-law")
    print(f"Civil law prompts: {len(civil_law_prompts)}")

    # List all common law prompts
    common_law_prompts = registry.list_by_legal_system("common-law")
    print(f"Common law prompts: {len(common_law_prompts)}")

    # Show prompt types available for civil law
    print("\nCivil law prompt types:")
    types = set()
    for prompt in civil_law_prompts:
        info = prompt.get_info()
        types.add(info["prompt_type"])
    for prompt_type in sorted(types):
        print(f"  - {prompt_type}")


def example_india_specific():
    """Example accessing India-specific prompts."""
    print("\n" + "=" * 80)
    print("Example 5: India-Specific Prompts")
    print("=" * 80 + "\n")

    # Using legacy API
    prompt_module = get_prompt_module(
        jurisdiction="Common-law jurisdiction",
        prompt_type="analysis",
        specific_jurisdiction="India",
    )

    # Access India-specific prompts
    if hasattr(prompt_module, "COL_ISSUE_PROMPT"):
        print("✓ India-specific COL_ISSUE_PROMPT available")
        template = prompt_module.COL_ISSUE_PROMPT
        print(f"  Template length: {len(template)} characters")

    # Using registry API
    registry = get_registry()
    india_prompts = registry.list_by_jurisdiction("india")
    print(f"\n✓ Found {len(india_prompts)} India-specific prompts in registry")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("PROMPT MANAGEMENT SYSTEM - EXAMPLES")
    print("=" * 80)

    try:
        example_legacy_api()
        example_list_prompts()
        example_direct_registry()
        example_query_by_system()
        example_india_specific()

        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
