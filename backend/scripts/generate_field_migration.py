import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pydantic.alias_generators import to_camel

from app.mapping.configs import ALL_MAPPINGS
from app.schemas.mapping_schema import MappingConfig

SKIP_FIELDS = {"source_table", "id", "rank"}
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "field-migration")


def to_snake(name: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9]", "_", name)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_").lower()
    if not result or result[0].isdigit():
        result = f"f_{result}"
    return result


def extract_fields(config: MappingConfig) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    m = config.mappings

    for output_name, source_col in m.direct_mappings.items():
        if output_name in SKIP_FIELDS or output_name == "ID":
            continue
        snake = to_snake(output_name)
        fields.append(
            {
                "old_api": output_name,
                "camel": to_camel(snake),
                "snake": snake,
                "source": source_col,
                "type": "direct",
            }
        )

    for output_name, cond in m.conditional_mappings.items():
        if output_name in SKIP_FIELDS:
            continue
        snake = to_snake(output_name)
        fields.append(
            {
                "old_api": output_name,
                "camel": to_camel(snake),
                "snake": snake,
                "source": f"COALESCE({cond.primary}, {cond.fallback})",
                "type": "conditional",
            }
        )

    for output_name, bool_map in m.boolean_mappings.items():
        snake = to_snake(output_name)
        fields.append(
            {
                "old_api": output_name,
                "camel": to_camel(snake),
                "snake": snake,
                "source": f"{bool_map.source_field} (boolean: {bool_map.true_value}/{bool_map.false_value})",
                "type": "boolean",
            }
        )

    for output_name, complex_map in m.complex_mappings.items():
        snake = to_snake(output_name)
        fields.append(
            {
                "old_api": output_name,
                "camel": to_camel(snake),
                "snake": snake,
                "source": f"{complex_map.source_field} ({complex_map.type}.{complex_map.operation})",
                "type": "complex",
            }
        )

    for nested_key, nested in m.nested_mappings.items():
        prefix = nested.source_array
        idx_note = f"[{nested.index}]" if nested.index is not None else "[*]"

        if nested.mappings:
            for output_name, field_path in nested.mappings.items():
                if output_name in SKIP_FIELDS:
                    continue
                snake = to_snake(output_name)
                fields.append(
                    {
                        "old_api": output_name,
                        "camel": to_camel(snake),
                        "snake": snake,
                        "source": f"{prefix}{idx_note}.{field_path}",
                        "type": "nested",
                    }
                )

        if nested.array_operations:
            for output_name, arr_op in nested.array_operations.items():
                snake = to_snake(output_name)
                sep_repr = repr(arr_op.separator.value if hasattr(arr_op.separator, "value") else arr_op.separator)
                fields.append(
                    {
                        "old_api": output_name,
                        "camel": to_camel(snake),
                        "snake": snake,
                        "source": f"{prefix}[*].{arr_op.field} (joined by {sep_repr})",
                        "type": "nested/array_join",
                    }
                )

        if nested.conditional_mappings:
            for output_name, cond in nested.conditional_mappings.items():
                snake = to_snake(output_name)
                fields.append(
                    {
                        "old_api": output_name,
                        "camel": to_camel(snake),
                        "snake": snake,
                        "source": f"{prefix}{idx_note}.COALESCE({cond.primary}, {cond.fallback})",
                        "type": "nested/conditional",
                    }
                )

        if nested.boolean_mappings:
            for output_name, bool_map in nested.boolean_mappings.items():
                snake = to_snake(output_name)
                fields.append(
                    {
                        "old_api": output_name,
                        "camel": to_camel(snake),
                        "snake": snake,
                        "source": f"{prefix}{idx_note}.{bool_map.source_field} (boolean)",
                        "type": "nested/boolean",
                    }
                )

    for user_key, user_map in m.user_mappings.items():
        for output_name, user_field in user_map.user_fields.items():
            snake = to_snake(output_name)
            fields.append(
                {
                    "old_api": output_name,
                    "camel": to_camel(snake),
                    "snake": snake,
                    "source": f"{user_map.source_field}.{user_field}",
                    "type": "user",
                }
            )

    return fields


def table_name_to_filename(table_name: str) -> str:
    return table_name.lower().replace(" ", "_") + ".md"


def generate_markdown(table_name: str, config: MappingConfig) -> str:
    fields = extract_fields(config)
    lines = [
        f"# {table_name} -- Field Migration Reference",
        "",
        "| Old API field name | New API field name (camelCase) | Python/SQL field name (snake_case) | NocoDB source | Mapping type |",
        "|---|---|---|---|---|",
    ]

    base_fields = [
        {
            "old_api": "source_table",
            "camel": "sourceTable",
            "snake": "source_table",
            "source": "source_table (injected)",
            "type": "base",
        },
        {"old_api": "id", "camel": "id", "snake": "id", "source": "CoLD_ID", "type": "base"},
        {"old_api": "rank", "camel": "rank", "snake": "rank", "source": "rank (search score)", "type": "base"},
    ]

    for f in base_fields + fields:
        lines.append(
            f"| `{f['old_api']}` | `{f['camel']}` | `{f['snake']}` | `{f['source']}` | {f['type']} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    index_lines = [
        "# Field Migration Reference",
        "",
        "Auto-generated mapping from old API field names to new camelCase API names.",
        "Used for mechanical find-and-replace across frontend `.vue` and `.ts` files.",
        "",
        "## Tables",
        "",
    ]

    for table_name, config in sorted(ALL_MAPPINGS.items()):
        filename = table_name_to_filename(table_name)
        md = generate_markdown(table_name, config)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(md)
        index_lines.append(f"- [{table_name}]({filename})")
        print(f"Generated {filename}")

    index_path = os.path.join(OUTPUT_DIR, "README.md")
    with open(index_path, "w") as f:
        f.write("\n".join(index_lines) + "\n")
    print(f"\nGenerated README.md index with {len(ALL_MAPPINGS)} tables")


if __name__ == "__main__":
    main()
