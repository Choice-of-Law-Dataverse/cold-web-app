from __future__ import annotations

import re
import sys
import textwrap
from datetime import UTC, datetime
from pathlib import Path

from alembic_views.detail_config import ALL_RELATION_KEYS, ENTITIES, SCHEMA, EntityConfig, Relation

VERSIONS_DIR = Path(__file__).parent / "versions"


def _relation_sql(key: str, rel: Relation) -> str:
    if rel.custom_sql:
        return f"""            '{key}', COALESCE((
                {rel.custom_sql}
            ), '[]'::jsonb)"""
    return f"""            '{key}', COALESCE((
                SELECT jsonb_agg(to_jsonb(r.*))
                FROM data_views.{rel.rel_view} r
                JOIN {SCHEMA}."{rel.m2m_table}" m ON m."{rel.rel_fk}" = r.id
                WHERE m."{rel.entity_fk}" = v_id
            ), '[]'::jsonb)"""


def _empty_relation_sql(key: str) -> str:
    return f"            '{key}', '[]'::jsonb"


def _entity_block(entity: EntityConfig, is_first: bool) -> str:
    keyword = "IF" if is_first else "ELSIF"
    lines: list[str] = []
    lines.append(f"    {keyword} p_table_name = '{entity.display_name}' THEN")
    lines.append(entity.base_query.rstrip())
    lines.append("")

    rel_lines: list[str] = []
    populated_keys = set(entity.relations.keys())
    for key in ALL_RELATION_KEYS:
        if key == entity.display_name.lower().replace(" ", "_"):
            rel_lines.append(_empty_relation_sql(key))
            continue
        if key in populated_keys:
            rel_lines.append(_relation_sql(key, entity.relations[key]))
        else:
            rel_lines.append(_empty_relation_sql(key))

    lines.append("        SELECT jsonb_build_object(")
    lines.append(",\n".join(rel_lines))
    lines.append("        ) INTO v_rels;")
    lines.append("")
    lines.append(f"        RETURN QUERY SELECT '{entity.display_name}'::TEXT, v_id, v_cold_id, v_base, v_rels;")
    return "\n".join(lines)


def generate_detail_function_sql() -> str:
    blocks = [_entity_block(entity, i == 0) for i, entity in enumerate(ENTITIES)]
    body = "\n\n    ".join(blocks)

    return textwrap.dedent(f"""\
        DROP FUNCTION IF EXISTS data_views.get_entity_detail(TEXT, TEXT);

        CREATE OR REPLACE FUNCTION data_views.get_entity_detail(
            p_table_name TEXT,
            p_cold_id TEXT
        )
        RETURNS TABLE (
            source_table TEXT,
            record_id INTEGER,
            cold_id TEXT,
            base_record JSONB,
            relations JSONB
        ) AS $$
        DECLARE
            v_id INTEGER;
            v_cold_id TEXT;
            v_base JSONB;
            v_rels JSONB;
        BEGIN
            {body}

            ELSE
                RAISE EXCEPTION 'Unsupported table_name: %', p_table_name;
            END IF;
        END;
        $$ LANGUAGE plpgsql STABLE;""")


def _find_latest_revision() -> str:
    latest = ""
    for path in VERSIONS_DIR.glob("*.py"):
        match = re.match(r"(\d+)_", path.name)
        if match and match.group(1) > latest:
            latest = match.group(1)
    return latest


def _generate_migration_file(description: str) -> Path:
    sql = generate_detail_function_sql()
    down_revision = _find_latest_revision()
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d%H%M")
    slug = description.replace(" ", "_")
    revision = timestamp
    filename = f"{timestamp}_{slug}.py"
    filepath = VERSIONS_DIR / filename

    content = f'''from __future__ import annotations

from alembic import op

revision = "{revision}"
down_revision = "{down_revision}"
branch_labels = None
depends_on = None

DETAIL_FUNCTION = """
{sql}
"""


def upgrade() -> None:
    op.execute(DETAIL_FUNCTION)


def downgrade() -> None:
    pass
'''

    filepath.write_text(content)
    return filepath


def _print_check() -> None:
    sql = generate_detail_function_sql()
    print(f"Generated SQL: {len(sql)} chars, {sql.count(chr(10))} lines")
    print(f"Entities: {len(ENTITIES)}")
    for e in ENTITIES:
        populated = len(e.relations)
        empty = len(ALL_RELATION_KEYS) - populated
        self_ref = 1 if e.display_name.lower().replace(" ", "_") in ALL_RELATION_KEYS else 0
        print(f"  {e.display_name}: {populated} populated, {empty - self_ref} empty, {self_ref} self-ref")


if __name__ == "__main__":
    if "--check" in sys.argv:
        _print_check()
    elif "--migration" in sys.argv:
        desc_idx = sys.argv.index("--migration") + 1
        desc = sys.argv[desc_idx] if desc_idx < len(sys.argv) else "update_entity_detail"
        filepath = _generate_migration_file(desc)
        print(f"Created: {filepath}")
    else:
        print(generate_detail_function_sql())
