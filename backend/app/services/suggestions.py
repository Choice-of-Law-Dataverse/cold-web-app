import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
try:
    import jwt  # type: ignore
except Exception:  # pragma: no cover - optional dependency resolution in some editors
    jwt = None  # type: ignore

from app.config import config


class SuggestionService:
    """Stores suggestions in per-type Postgres tables using the default schema from the DSN."""

    def __init__(self) -> None:
        # Prefer dedicated connection string for suggestions DB
        conn = config.SUGGESTIONS_SQL_CONN_STRING or config.SQL_CONN_STRING
        if not conn:
            raise RuntimeError("No SQL connection string configured for suggestions storage")

        self.engine = sa.create_engine(conn)
        # Use default schema (search_path) of the provided connection
        self.metadata = sa.MetaData()

        # Define per-type suggestion tables with JSONB payloads
        self.tables: Dict[str, sa.Table] = {
            "generic": sa.Table(
                "suggestions_generic",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            "court_decisions": sa.Table(
                "suggestions_court_decisions",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            "domestic_instruments": sa.Table(
                "suggestions_domestic_instruments",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            "regional_instruments": sa.Table(
                "suggestions_regional_instruments",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            "international_instruments": sa.Table(
                "suggestions_international_instruments",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            "literature": sa.Table(
                "suggestions_literature",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
        }

        # Ensure all tables exist
        self.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _get_token_sub(self, authorization: Optional[str]) -> Optional[str]:
        if not authorization:
            return None
        try:
            parts = authorization.split()
            if len(parts) >= 2 and parts[0].lower() == "bearer" and jwt is not None:
                decoded = jwt.decode(parts[1], config.JWT_SECRET, algorithms=["HS256"])  # type: ignore[attr-defined]
                return str(decoded.get("sub")) if isinstance(decoded, dict) else None
        except Exception:
            return None
        return None

    @staticmethod
    def _to_jsonable(obj: Any) -> Any:
        """Recursively convert payload to JSON-serializable primitives."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            # Prefer float for JSON
            return float(obj)
        if isinstance(obj, dict):
            return {str(k): SuggestionService._to_jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [SuggestionService._to_jsonable(v) for v in obj]
        # Fallback to string representation
        return str(obj)

    def save_suggestion(
        self,
        payload: Dict[str, Any],
        *,
        table: str = "generic",
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: Optional[str] = None,
        authorization: Optional[str] = None,
    ) -> int:
        token_sub = self._get_token_sub(authorization)
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")

        with self.Session() as session:
            safe_payload = self._to_jsonable(payload)
            stmt = (
                target.insert()
                .values(
                    payload=safe_payload,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    source=source,
                    token_sub=token_sub,
                )
                .returning(target.c.id)
            )
            result = session.execute(stmt)
            session.commit()
            new_id = result.scalar_one()
            return int(new_id)
