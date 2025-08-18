import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from typing import Any, Dict
from datetime import datetime, date

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

    @staticmethod
    def _parse_date(val: Any) -> Any:
        if val is None:
            return None
        if isinstance(val, (date, datetime)):
            return val if isinstance(val, date) else val.date()
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val).date()
            except Exception:
                return val
        return val

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        # Reflect table structure lazily
        table = sa.Table(table_name, self.metadata, autoload_with=self.engine)
        # Coerce date-like fields to date objects if column is of type Date
        coerced: Dict[str, Any] = {}
        for key, value in data.items():
            col = table.c.get(key) if hasattr(table.c, key) else None
            # heuristically handle date columns by name as well
            if key.lower().endswith("date") or key.lower().endswith("_date"):
                coerced[key] = self._parse_date(value)
            else:
                coerced[key] = value
        with self.Session() as session:
            stmt = table.insert().values(**coerced).returning(table.c.id)
            result = session.execute(stmt)
            session.commit()
            new_id = result.scalar_one()
            return int(new_id)
