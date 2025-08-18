import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict
from datetime import datetime, date
from decimal import Decimal

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
    COLUMN_MAPPINGS: Dict[str, Dict[str, str]] = {
        "Court_Decisions": {
            "case_citation": "Case_Citation",
            "official_source_url": "Official_Source__URL_",
            "official_source_pdf": "Official_Source__PDF_",
            "abstract": "Abstract",
            "internal_notes": "Internal_Notes",
            "english_translation": "English_Translation",
            "pil_provisions": "PIL_Provisions",
            "choice_of_law_issue": "Choice_of_Law_Issue",
            "courts_position": "Court_s_Position",
            "relevant_legal_provisions_text": "Text_of_the_Relevant_Legal_Provisions",
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
        # Add other table mappings as needed
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

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        # Reflect table structure lazily
        table = sa.Table(table_name, self.metadata, autoload_with=self.engine)
        valid_columns = {col.name for col in table.columns}
        # Select mapping for this table if available
        mapping = self.COLUMN_MAPPINGS.get(table_name, {})

        coerced: Dict[str, Any] = {}
        for key, value in data.items():
            db_key = mapping.get(key, key)
            if db_key not in valid_columns:
                # Skip keys that don't exist on the target table
                continue
            col = table.c[db_key]
            # Treat empty string as NULL for non-text columns
            if isinstance(col.type, (sa.Integer, sa.Numeric, sa.Date, sa.Boolean)) and isinstance(value, str) and value.strip() == "":
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
