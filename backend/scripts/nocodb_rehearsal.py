"""Verify NocoDB's physical schema and application write paths on a local clone."""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.reflection import Inspector

DEFAULT_SCHEMA = "p1q5x3pj29vkrdr"
DEFAULT_DATA_VIEWS_SCHEMA = "data_views"
EXPECTED_DATA_VIEW_OBJECTS = 69

MAPPING_TARGETS = {
    "Case_Analyzer": "Court_Decisions",
}

LINK_TABLES = {
    "_nc_m2m_Jurisdictions_Court_Decisions": {
        "Court_Decisions_id",
        "Jurisdictions_id",
    },
    "_nc_m2m_Jurisdictions_Domestic_Instru": {
        "Domestic_Instruments_id",
        "Jurisdictions_id",
    },
    "_nc_m2m_Jurisdictions_Literature": {
        "Literature_id",
        "Jurisdictions_id",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "smoke"))
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--data-views-schema", default=DEFAULT_DATA_VIEWS_SCHEMA)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--nocodb-base-url")
    parser.add_argument("--nocodb-api-token")
    return parser.parse_args()


def quote(connection: Connection, identifier: str) -> str:
    return connection.dialect.identifier_preparer.quote(identifier)


def table_count(connection: Connection, schema: str, table: str) -> int:
    statement = sa.text(f"SELECT count(*) FROM {quote(connection, schema)}.{quote(connection, table)}")
    return int(connection.execute(statement).scalar_one())


def refresh_materialized_views(connection: Connection, data_views_schema: str) -> None:
    schema = quote(connection, data_views_schema)
    connection.execute(sa.text(f"SELECT {schema}.refresh_all_materialized_views()"))
    connection.commit()


def collect_data_view_objects(connection: Connection, data_views_schema: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        sa.text(
            """
            SELECT
                CASE c.relkind
                    WHEN 'm' THEN 'materialized_view'
                    WHEN 'v' THEN 'view'
                END AS object_type,
                c.relname AS object_name,
                NULL::text AS arguments
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = :schema
              AND c.relkind IN ('m', 'v')

            UNION ALL

            SELECT
                'function' AS object_type,
                p.proname AS object_name,
                pg_get_function_identity_arguments(p.oid) AS arguments
            FROM pg_proc AS p
            JOIN pg_namespace AS n ON n.oid = p.pronamespace
            WHERE n.nspname = :schema

            ORDER BY object_type, object_name, arguments
            """
        ),
        {"schema": data_views_schema},
    ).mappings()
    return [dict(row) for row in rows]


def validate_column_mappings(inspector: Inspector, schema: str) -> list[dict[str, str]]:
    os.environ.setdefault("SQL_CONN_STRING", "unused")
    os.environ.setdefault("NOCODB_POSTGRES_SCHEMA", schema)
    from app.services.moderation_writer import MainDBWriter

    missing: list[dict[str, str]] = []
    for mapping_name, mappings in MainDBWriter.COLUMN_MAPPINGS.items():
        table = MAPPING_TARGETS.get(mapping_name, mapping_name)
        columns = {column["name"] for column in inspector.get_columns(table, schema=schema)}
        for column in sorted(set(mappings.values())):
            if column not in columns:
                missing.append({"mapping": mapping_name, "table": table, "column": column})
    return missing


def validate_link_tables(inspector: Inspector, schema: str) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    tables = set(inspector.get_table_names(schema=schema))
    for table, expected_columns in LINK_TABLES.items():
        if table not in tables:
            missing.append({"table": table, "missing_columns": sorted(expected_columns)})
            continue
        actual_columns = {column["name"] for column in inspector.get_columns(table, schema=schema)}
        absent_columns = expected_columns - actual_columns
        if absent_columns:
            missing.append({"table": table, "missing_columns": sorted(absent_columns)})
    return missing


def collect_snapshot(engine: Engine, schema: str, data_views_schema: str) -> dict[str, Any]:
    inspector = sa.inspect(engine)
    with engine.connect() as connection:
        refresh_materialized_views(connection, data_views_schema)

        data_view_objects = collect_data_view_objects(connection, data_views_schema)
        if len(data_view_objects) != EXPECTED_DATA_VIEW_OBJECTS:
            raise RuntimeError(
                f"Expected {EXPECTED_DATA_VIEW_OBJECTS} objects in {data_views_schema}, found {len(data_view_objects)}"
            )

        data_view_counts: dict[str, int] = {}
        for object_data in data_view_objects:
            if object_data["object_type"] == "function":
                continue
            name = str(object_data["object_name"])
            count = table_count(connection, data_views_schema, name)
            data_view_counts[name] = count
            if count == 0:
                raise RuntimeError(f"{data_views_schema}.{name} returned no rows")

        base_table_counts = {
            table: table_count(connection, schema, table) for table in sorted(inspector.get_table_names(schema=schema))
        }

        schema_name = quote(connection, schema)
        invalid_alpha_codes = int(
            connection.execute(
                sa.text(
                    f"""
                    SELECT count(*)
                    FROM {schema_name}."Jurisdictions"
                    WHERE "Alpha_3_Code" IS NOT NULL
                      AND "Alpha_3_Code" <> upper("Alpha_3_Code")
                    """
                )
            ).scalar_one()
        )
        sample_alpha_code = connection.execute(
            sa.text(
                f"""
                SELECT "Alpha_3_Code"
                FROM {schema_name}."Jurisdictions"
                WHERE "Alpha_3_Code" IS NOT NULL
                ORDER BY id
                LIMIT 1
                """
            )
        ).scalar_one()
        exact_alpha_matches = int(
            connection.execute(
                sa.text(
                    f"""
                    SELECT count(*)
                    FROM {schema_name}."Jurisdictions"
                    WHERE "Alpha_3_Code" = :alpha_code
                    """
                ),
                {"alpha_code": sample_alpha_code},
            ).scalar_one()
        )

    missing_columns = validate_column_mappings(inspector, schema)
    missing_link_tables = validate_link_tables(inspector, schema)
    if missing_columns:
        raise RuntimeError(f"COLUMN_MAPPINGS columns are missing: {missing_columns}")
    if missing_link_tables:
        raise RuntimeError(f"Junction tables or key columns are missing: {missing_link_tables}")
    if invalid_alpha_codes:
        raise RuntimeError(f"Found {invalid_alpha_codes} lowercase or mixed-case jurisdiction codes")
    if exact_alpha_matches < 1:
        raise RuntimeError("A plain '=' jurisdiction-code lookup returned no rows")

    return {
        "base_table_counts": base_table_counts,
        "column_mappings_valid": True,
        "data_view_counts": data_view_counts,
        "data_view_objects": data_view_objects,
        "jurisdiction_filter": {
            "invalid_uppercase_codes": invalid_alpha_codes,
            "sample_exact_match_count": exact_alpha_matches,
        },
        "link_tables_valid": True,
    }


def first_jurisdiction(connection: Connection, schema: str) -> tuple[int, str]:
    schema_name = quote(connection, schema)
    row = connection.execute(
        sa.text(
            f"""
            SELECT id, "Alpha_3_Code"
            FROM {schema_name}."Jurisdictions"
            WHERE "Alpha_3_Code" IS NOT NULL
            ORDER BY id
            LIMIT 1
            """
        )
    ).one()
    return int(row[0]), str(row[1])


def cleanup_court_decision(engine: Engine, schema: str, record_id: int) -> None:
    with engine.begin() as connection:
        schema_name = quote(connection, schema)
        connection.execute(
            sa.text(
                f"""
                DELETE FROM {schema_name}."_nc_m2m_Jurisdictions_Court_Decisions"
                WHERE "Court_Decisions_id" = :record_id
                """
            ),
            {"record_id": record_id},
        )
        connection.execute(
            sa.text(f'DELETE FROM {schema_name}."Court_Decisions" WHERE id = :record_id'),
            {"record_id": record_id},
        )


def direct_write_smoke(engine: Engine, database_url: str, schema: str) -> dict[str, Any]:
    os.environ["SQL_CONN_STRING"] = database_url
    os.environ["NOCODB_POSTGRES_SCHEMA"] = schema
    from app.services.moderation_writer import MainDBWriter

    with engine.connect() as connection:
        jurisdiction_id, jurisdiction_code = first_jurisdiction(connection, schema)

    marker = f"NocoDB rehearsal direct write {uuid.uuid4()}"
    writer = MainDBWriter()
    record_id: int | None = None
    try:
        record_id = writer.insert_record("Court_Decisions", {"case_citation": marker})
        writer.link_jurisdictions("Court_Decisions", record_id, jurisdiction_code)
        with engine.connect() as connection:
            schema_name = quote(connection, schema)
            link_count = int(
                connection.execute(
                    sa.text(
                        f"""
                        SELECT count(*)
                        FROM {schema_name}."_nc_m2m_Jurisdictions_Court_Decisions"
                        WHERE "Court_Decisions_id" = :record_id
                          AND "Jurisdictions_id" = :jurisdiction_id
                        """
                    ),
                    {"record_id": record_id, "jurisdiction_id": jurisdiction_id},
                ).scalar_one()
            )
        if link_count != 1:
            raise RuntimeError("MainDBWriter did not create the jurisdiction link")
        return {"record_created": True, "jurisdiction_linked": True}
    finally:
        if record_id is not None:
            cleanup_court_decision(engine, schema, record_id)


def api_smoke(engine: Engine, schema: str, base_url: str, api_token: str) -> dict[str, Any]:
    from app.services.nocodb import (
        COURT_DECISIONS_JURISDICTIONS_FIELD_ID,
        COURT_DECISIONS_TABLE_ID,
        NocoDBService,
    )

    with engine.connect() as connection:
        jurisdiction_id, jurisdiction_code = first_jurisdiction(connection, schema)

    service = NocoDBService(base_url=base_url, api_token=api_token)
    jurisdiction_ids = service.list_jurisdictions(jurisdiction_code)
    if jurisdiction_id not in jurisdiction_ids:
        raise RuntimeError("NocoDB list/read path did not resolve the sampled jurisdiction")

    marker = f"NocoDB rehearsal API write {uuid.uuid4()}"
    record_id: int | None = None
    try:
        created = service.create_row(COURT_DECISIONS_TABLE_ID, {"Case_Citation": marker})
        raw_record_id = created.get("id") or created.get("Id")
        if raw_record_id is None:
            raise RuntimeError(f"NocoDB create response had no record ID: {created}")
        record_id = int(raw_record_id)
        service.link_records(
            table_id=COURT_DECISIONS_TABLE_ID,
            record_id=record_id,
            field_id=COURT_DECISIONS_JURISDICTIONS_FIELD_ID,
            linked_record_ids=[jurisdiction_id],
        )
        fetched = service.get_row(COURT_DECISIONS_TABLE_ID, str(record_id))
        fetched_record_id = fetched.get("id") or fetched.get("Id")
        if fetched_record_id is None or int(fetched_record_id) != record_id:
            raise RuntimeError(f"NocoDB record read returned the wrong record ID: {fetched_record_id}")
        return {
            "record_created": True,
            "record_read": True,
            "jurisdiction_linked": True,
        }
    finally:
        if record_id is not None:
            cleanup_court_decision(engine, schema, record_id)


def run() -> int:
    args = parse_args()
    engine = sa.create_engine(args.database_url)
    try:
        if args.command == "snapshot":
            result = collect_snapshot(engine, args.schema, args.data_views_schema)
        else:
            result: dict[str, Any] = {
                "direct_write": direct_write_smoke(engine, args.database_url, args.schema),
            }
            if args.nocodb_base_url and args.nocodb_api_token:
                result["nocodb_api"] = api_smoke(
                    engine,
                    args.schema,
                    args.nocodb_base_url,
                    args.nocodb_api_token,
                )
            elif args.nocodb_base_url or args.nocodb_api_token:
                raise RuntimeError("Both --nocodb-base-url and --nocodb-api-token are required for the API smoke test")
            else:
                result["nocodb_api"] = "skipped: no local base URL and API token supplied"

        serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized)
        else:
            sys.stdout.write(serialized)
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(run())
