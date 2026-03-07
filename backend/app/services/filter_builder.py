import re
from typing import Any

from pydantic.alias_generators import to_snake


def _camel_to_snake(name: str) -> str:
    return to_snake(name)


def _is_jsonb_path(column: str) -> bool:
    return "." in column


def build_filter_clause(
    alias: str,
    filters: list[Any],
) -> tuple[str, dict[str, Any]]:
    if not filters:
        return "", {}

    clauses: list[str] = []
    params: dict[str, Any] = {}

    for i, f in enumerate(filters):
        col = getattr(f, "column", None) if hasattr(f, "column") else f.get("column")
        raw_val = getattr(f, "value", None) if hasattr(f, "value") else f.get("value")
        if col is None:
            continue

        snake_col = _camel_to_snake(col)

        conv_values = raw_val if isinstance(raw_val, list) else [raw_val]

        or_parts: list[str] = []
        for j, v in enumerate(conv_values):
            p_name = f"p_{i}_{j}"

            if _is_jsonb_path(snake_col):
                arr_name, field_name = snake_col.split(".", 1)
                arr_sql = f'{alias}."{arr_name}"'
                field_literal = field_name.replace("'", "''")
                if isinstance(v, str):
                    or_parts.append(
                        f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem "
                        f"WHERE elem->>'{field_literal}' ILIKE '%' || :{p_name} || '%')"
                    )
                    params[p_name] = v
                elif isinstance(v, bool):
                    or_parts.append(
                        f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem "
                        f"WHERE (elem->>'{field_literal}')::boolean = :{p_name})"
                    )
                    params[p_name] = v
                elif isinstance(v, (int, float)):
                    or_parts.append(
                        f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem "
                        f"WHERE (elem->>'{field_literal}')::numeric = :{p_name})"
                    )
                    params[p_name] = v
                else:
                    or_parts.append(
                        f"EXISTS (SELECT 1 FROM jsonb_array_elements({arr_sql}) elem "
                        f"WHERE elem->>'{field_literal}' = :{p_name})"
                    )
                    params[p_name] = str(v)
            else:
                safe_col = re.sub(r"[^a-zA-Z0-9_]", "", snake_col)
                col_sql = f'{alias}."{safe_col}"'
                if isinstance(v, str):
                    or_parts.append(f"{col_sql} ILIKE '%' || :{p_name} || '%'")
                    params[p_name] = v
                elif isinstance(v, bool):
                    or_parts.append(f"{col_sql} = :{p_name}")
                    params[p_name] = v
                elif isinstance(v, (int, float)):
                    or_parts.append(f"{col_sql} = :{p_name}")
                    params[p_name] = v
                else:
                    or_parts.append(f"{col_sql}::text = :{p_name}")
                    params[p_name] = str(v)

        if or_parts:
            clauses.append("(" + " OR ".join(or_parts) + ")")

    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, params
