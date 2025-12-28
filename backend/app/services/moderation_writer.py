from datetime import date, datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.config import config


class MainDBWriter:
    def __init__(self) -> None:
        conn = config.SQL_CONN_STRING
        if not conn:
            raise RuntimeError("SQL_CONN_STRING not configured for main DB")
        self.engine = sa.create_engine(conn)
        # Target schema from env (NocoDB schema)
        self.schema = config.NOCODB_POSTGRES_SCHEMA
        self.metadata = sa.MetaData(schema=self.schema)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    # Mapping from suggestion payload keys (snake_case) to NocoDB column names (Pascal/Title case)
    COLUMN_MAPPINGS: dict[str, dict[str, str]] = {
        "Court_Decisions": {
            "case_citation": "Case_Citation",
            "official_source_url": "Official_Source__URL_",
            # removed: official_source_pdf
            "abstract": "Abstract",
            "internal_notes": "Internal_Notes",
            "english_translation": "English_Translation",
            "pil_provisions": "PIL_Provisions",
            "choice_of_law_issue": "Choice_of_Law_Issue",
            "courts_position": "Court_s_Position",
            "text_of_relevant_legal_provisions": "Text_of_the_Relevant_Legal_Provisions",
            "translated_excerpt": "Translated_Excerpt",
            "quote": "Quote",
            "copyright_issues": "Copyright_Issues",
            "relevant_facts": "Relevant_Facts",
            "id_number": "ID_number",
            "case_rank": "Case_Rank",
            "decision_date": "Date_of_Judgment",
            "original_text": "Original_Text",
            "created": "Created",
            "last_modified": "Last_Modified",
            "last_modified_by": "Last_Modified_By",
            "added_by": "Added_By",
            "date": "Date",
            "case_title": "Case_Title",
            "instance": "Instance",
            "official_keywords": "Official_Keywords",
            "publication_date_iso": "Publication_Date_ISO",
            "created_by": "Created_By",
        },
        # Domestic Instruments
        "Domestic_Instruments": {
            "title_en": "Title__in_English_",
            "official_title": "Official_Title",
            "entry_into_force": "Entry_Into_Force",
            "source_url": "Source__URL_",
            # removed: source_pdf
            "publication_date": "Publication_Date",
            "abbreviation": "Abbreviation",
            "status": "Status",
            "compatible_hcch_principles": "Compatible_With_the_HCCH_Principles_",
            "compatible_uncitral_model_law": "Compatible_With_the_UNCITRAL_Model_Law_",
            "date_year_of_entry_into_force": "Date",
        },
        # Regional Instruments
        "Regional_Instruments": {
            "abbreviation": "Abbreviation",
            "title": "Title",
            "url": "URL",
            # removed: attachment
            "instrument_date": "Date",
        },
        # International Instruments
        "International_Instruments": {
            "name": "Name",
            "url": "URL",
            # removed: attachment
            "instrument_date": "Date",
        },
        # Literature
        "Literature": {
            "publication_year": "Publication_Year",
            "author": "Author",
            "title": "Title",
            "publication_title": "Publication_Title",
            "isbn": "ISBN",
            "issn": "ISSN",
            "doi": "DOI",
            "url": "Url",
            "publication_date": "Date",
        },
        # Case Analyzer (maps normalized fields to Court_Decisions columns)
        # Note: Some fields are combined into Internal_Notes via prepare_case_analyzer_for_court_decisions()
        "Case_Analyzer": {
            "case_citation": "Case_Citation",
            "date": "Date_of_Judgment",
            "abstract": "Abstract",
            "relevant_facts": "Relevant_Facts",
            "pil_provisions": "PIL_Provisions",
            "choice_of_law_issue": "Choice_of_Law_Issue",
            "courts_position": "Court_s_Position",
            "internal_notes": "Internal_Notes",
            # jurisdiction is used for linking, not direct column mapping
        },
    }

    @staticmethod
    def _parse_date(val: Any) -> Any:
        if val is None:
            return None
        if isinstance(val, (date, datetime)):
            return val if isinstance(val, date) else val.date()
        if isinstance(val, str):
            if not val.strip():
                return None
            try:
                return datetime.fromisoformat(val).date()
            except Exception:
                return val
        return val

    @staticmethod
    def _to_bool(val: Any) -> Any:
        if val is None or isinstance(val, bool):
            return val
        if isinstance(val, str):
            s = val.strip().lower()
            if s in {"true", "1", "yes", "y"}:
                return True
            if s in {"false", "0", "no", "n"}:
                return False
            if s == "":
                return None
        return val

    @staticmethod
    def _to_number(val: Any, integer: bool) -> Any:
        if val is None or isinstance(val, (int, float, Decimal)):
            return int(val) if integer and isinstance(val, (int, float, Decimal)) else val
        if isinstance(val, str):
            s = val.strip()
            if s == "":
                return None
            try:
                return int(s) if integer else float(s)
            except Exception:
                return val
        return val

    def insert_record(self, table_name: str, data: dict[str, Any]) -> int:
        # Reflect table structure lazily
        table = sa.Table(table_name, self.metadata, autoload_with=self.engine)
        valid_columns = {col.name for col in table.columns}
        # Select mapping for this table if available
        mapping = self.COLUMN_MAPPINGS.get(table_name, {})

        coerced: dict[str, Any] = {}
        for key, value in data.items():
            db_key = mapping.get(key, key)
            if db_key not in valid_columns:
                # Skip keys that don't exist on the target table
                continue
            col = table.c[db_key]
            # Treat empty string as NULL for non-text columns
            if (
                isinstance(col.type, (sa.Integer, sa.Numeric, sa.Date, sa.Boolean))
                and isinstance(value, str)
                and value.strip() == ""
            ):
                coerced[db_key] = None
                continue
            # Coerce based on actual column type
            if isinstance(col.type, sa.Date):
                coerced[db_key] = self._parse_date(value)
            elif isinstance(col.type, sa.Boolean):
                coerced[db_key] = self._to_bool(value)
            elif isinstance(col.type, sa.Integer):
                coerced[db_key] = self._to_number(value, integer=True)
            elif isinstance(col.type, sa.Numeric):
                coerced[db_key] = self._to_number(value, integer=False)
            else:
                coerced[db_key] = value

        with self.Session() as session:
            if not coerced:
                raise ValueError(f"No valid columns to insert for table {table_name}")
            stmt = table.insert().values(**coerced).returning(table.c.id)
            result = session.execute(stmt)
            session.commit()
            new_id = result.scalar_one()
            return int(new_id)

    # Field labels for metadata in Internal_Notes
    CASE_ANALYZER_METADATA_LABELS = {
        "jurisdiction_type": "Jurisdiction Type",
        "choice_of_law_sections": "Choice of Law Section(s)",
        "theme": "Theme",
        "model": "AI Model",
    }

    def prepare_case_analyzer_for_court_decisions(self, normalized: dict[str, Any]) -> dict[str, Any]:
        """
        Transform normalized case_analyzer data into Court_Decisions-compatible format.
        Combines multiple metadata fields into Internal_Notes.
        """
        prepared: dict[str, Any] = {}
        
        # Direct mappings
        if normalized.get("case_citation"):
            prepared["case_citation"] = normalized["case_citation"]
        if normalized.get("date"):
            prepared["date"] = normalized["date"]
        if normalized.get("abstract"):
            prepared["abstract"] = normalized["abstract"]
        if normalized.get("relevant_facts"):
            prepared["relevant_facts"] = normalized["relevant_facts"]
        if normalized.get("pil_provisions"):
            prepared["pil_provisions"] = normalized["pil_provisions"]
        if normalized.get("choice_of_law_issue"):
            prepared["choice_of_law_issue"] = normalized["choice_of_law_issue"]
        if normalized.get("courts_position"):
            prepared["courts_position"] = normalized["courts_position"]
        
        # Store jurisdiction for linking (not a direct column)
        if normalized.get("jurisdiction"):
            prepared["jurisdiction"] = normalized["jurisdiction"]
        
        # Combine metadata fields into Internal_Notes
        notes_parts: list[str] = []
        for field_key, label in self.CASE_ANALYZER_METADATA_LABELS.items():
            if normalized.get(field_key):
                notes_parts.append(f"{label}: {normalized[field_key]}")
        if notes_parts:
            prepared["internal_notes"] = "\n".join(notes_parts)
        
        return prepared

    # --- Jurisdictions linking helpers ---
    def _resolve_jurisdiction_ids(self, raw_value: Any) -> list[int]:
        """Return a list of Jurisdictions.id resolved from user input.
        Accepts: integer id, numeric string id, ISO3 code (Alpha_3_Code), or Name; comma-separated list supported.
        """
        if raw_value is None:
            return []
        values: list[str]
        if isinstance(raw_value, (list, tuple)):
            values = [str(v) for v in raw_value]
        else:
            values = [s.strip() for s in str(raw_value).split(",")]
        values = [v for v in values if v]
        if not values:
            return []

        jur_table = sa.Table("Jurisdictions", self.metadata, autoload_with=self.engine)
        found: list[int] = []
        with self.Session() as session:
            for v in values:
                # Try numeric id first
                try:
                    vid = int(v)
                    # verify exists
                    q = sa.select(jur_table.c.id).where(jur_table.c.id == vid)
                    row = session.execute(q).scalar_one_or_none()
                    if row is not None:
                        found.append(int(row))
                        continue
                except Exception:
                    pass
                # Try ISO3 code (Alpha_3_Code)
                q = sa.select(jur_table.c.id).where(sa.func.lower(jur_table.c.Alpha_3_Code) == v.lower())
                row = session.execute(q).scalar_one_or_none()
                if row is not None:
                    found.append(int(row))
                    continue
                # Try exact name match (case-insensitive)
                q = sa.select(jur_table.c.id).where(sa.func.lower(jur_table.c.Name) == v.lower())
                row = session.execute(q).scalar_one_or_none()
                if row is not None:
                    found.append(int(row))
                    continue
        return found

    def link_jurisdictions(self, table_name: str, record_id: int, jurisdiction_value: Any) -> None:
        """Link one or more jurisdictions to a record using NocoDB m2m link tables.
        table_name: target main table (e.g., 'Court_Decisions')
        jurisdiction_value: input that can be an id, ISO3, Name, or comma-separated values.
        """
        link_map: dict[str, dict[str, str]] = {
            "Court_Decisions": {
                "link_table": "_nc_m2m_Jurisdictions_Court_Decisions",
                "left_key": "Court_Decisions_id",
                "right_key": "Jurisdictions_id",
            },
            "Domestic_Instruments": {
                "link_table": "_nc_m2m_Jurisdictions_Domestic_Instru",
                "left_key": "Domestic_Instruments_id",
                "right_key": "Jurisdictions_id",
            },
            "Literature": {
                "link_table": "_nc_m2m_Jurisdictions_Literature",
                "left_key": "Literature_id",
                "right_key": "Jurisdictions_id",
            },
        }
        meta = link_map.get(table_name)
        if not meta:
            return
        jur_ids = self._resolve_jurisdiction_ids(jurisdiction_value)
        if not jur_ids:
            return

        link_table = sa.Table(meta["link_table"], self.metadata, autoload_with=self.engine)
        left_col = link_table.c[meta["left_key"]]
        right_col = link_table.c[meta["right_key"]]
        with self.Session() as session:
            for jid in jur_ids:
                # Avoid duplicate link
                exists_q = sa.select(sa.literal(1)).where(sa.and_(left_col == record_id, right_col == jid)).limit(1)
                exists = session.execute(exists_q).scalar_one_or_none()
                if exists is None:
                    session.execute(link_table.insert().values({meta["left_key"]: record_id, meta["right_key"]: jid}))
            session.commit()
