from datetime import date, datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker

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
            raise RuntimeError(
                "No SQL connection string configured for suggestions storage"
            )

        self.engine = sa.create_engine(conn)
        # Use default schema (search_path) of the provided connection
        self.metadata = sa.MetaData()

        # Define per-type suggestion tables with JSONB payloads
        self.tables: dict[str, sa.Table] = {
            "generic": sa.Table(
                "suggestions_generic",
                self.metadata,
                sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
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
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
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
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
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
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
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
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
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
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=False,
                ),
                sa.Column("payload", JSONB, nullable=False),
                sa.Column("client_ip", sa.String(64), nullable=True),
                sa.Column("user_agent", sa.Text, nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("token_sub", sa.String(256), nullable=True),
                extend_existing=True,
            ),
            # Case Analyzer uses existing schema with a 'data' column, so autoload it
            "case_analyzer": sa.Table(
                "suggestions_case_analyzer",
                self.metadata,
                autoload_with=self.engine,
                extend_existing=True,
            ),
        }

        # Ensure all tables exist (will not alter existing ones)
        self.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _get_token_sub(self, authorization: str | None) -> str | None:
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
        payload: dict[str, Any],
        *,
        table: str = "generic",
        client_ip: str | None = None,
        user_agent: str | None = None,
        source: str | None = None,
        authorization: str | None = None,
    ) -> int:
        token_sub = self._get_token_sub(authorization)
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")

        with self.Session() as session:
            safe_payload = self._to_jsonable(payload)
            # Case analyzer table stores JSON in 'data' column
            if table == "case_analyzer":
                values: dict[str, Any] = {"data": safe_payload}
                if hasattr(target.c, "client_ip"):
                    values["client_ip"] = client_ip
                if hasattr(target.c, "user_agent"):
                    values["user_agent"] = user_agent
                if hasattr(target.c, "source"):
                    values["source"] = source
                if hasattr(target.c, "token_sub"):
                    values["token_sub"] = token_sub
                stmt = target.insert().values(**values).returning(target.c.id)
            else:
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

    def list_pending(self, table: str, limit: int = 100) -> list[dict]:
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")
        with self.Session() as session:
            if table == "case_analyzer":
                # Select raw 'data' and filter in Python for moderation status
                cols = [target.c.id]
                created_col = getattr(target.c, "created_at", None)
                if created_col is not None:
                    cols.append(created_col)
                data_col = getattr(target.c, "data", None)
                if data_col is None:
                    return []
                cols.append(data_col)
                # Optional meta columns
                username_col = getattr(target.c, "username", None)
                user_email_col = getattr(target.c, "user_email", None)
                model_col = getattr(target.c, "model", None)
                citation_col = getattr(target.c, "case_citation", None)
                source_col = getattr(target.c, "source", None)
                for c in (
                    username_col,
                    user_email_col,
                    model_col,
                    citation_col,
                    source_col,
                ):
                    if c is not None:
                        cols.append(c)
                query = sa.select(*cols)
                if created_col is not None:
                    query = query.order_by(created_col.desc())
                query = query.limit(
                    limit * 5
                )  # read more since we'll filter client-side
                rows = session.execute(query).mappings().all()

                results: list[dict] = []
                import json as _json

                for r in rows:
                    raw_data = r.get("data")
                    payload: Any
                    if isinstance(raw_data, dict):
                        payload = raw_data
                    else:
                        try:
                            payload = (
                                _json.loads(raw_data) if raw_data is not None else {}
                            )
                        except Exception:
                            payload = {}
                    status = (
                        payload.get("moderation_status")
                        if isinstance(payload, dict)
                        else None
                    )
                    if status in {"approved", "rejected"}:
                        continue
                    results.append(
                        {
                            "id": r["id"],
                            "created_at": r.get("created_at"),
                            "payload": payload,
                            "source": r.get("source")
                            if source_col is not None
                            else None,
                            "username": r.get("username")
                            if username_col is not None
                            else None,
                            "user_email": r.get("user_email")
                            if user_email_col is not None
                            else None,
                            "model": r.get("model") if model_col is not None else None,
                            "case_citation": r.get("case_citation")
                            if citation_col is not None
                            else None,
                        }
                    )
                return results[:limit]

            # Default flow uses JSONB 'payload'
            query = (
                sa.select(
                    target.c.id,
                    target.c.created_at,
                    target.c.payload,
                    target.c.source,
                )
                .where(
                    sa.or_(
                        ~target.c.payload.has_key("moderation_status"),  # type: ignore[attr-defined]
                        target.c.payload["moderation_status"].astext.is_(None),
                    )
                )
                .order_by(target.c.created_at.desc())
                .limit(limit)
            )
            rows = session.execute(query).mappings().all()
            return [dict(r) for r in rows]

    def mark_status(
        self,
        table: str,
        suggestion_id: int,
        status: str,
        moderator: str,
        note: str | None = None,
        merged_id: int | None = None,
    ) -> None:
        if status not in {"approved", "rejected"}:
            raise ValueError("status must be 'approved' or 'rejected'")
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")
        with self.Session() as session:
            if table == "case_analyzer":
                import json as _json

                sel = (
                    sa.select(target.c.data)
                    .where(target.c.id == suggestion_id)
                    .limit(1)
                )
                row = session.execute(sel).first()
                current: dict[str, Any]
                if row and isinstance(row[0], dict):
                    current = dict(row[0])
                else:
                    try:
                        current = _json.loads(row[0]) if row else {}
                    except Exception:
                        current = {}
                current["moderation_status"] = status
                current["moderated_by"] = moderator
                current["moderation_note"] = note or ""
                if merged_id is not None:
                    current["merged_record_id"] = int(merged_id)
                new_val = _json.dumps(self._to_jsonable(current))
                upd = (
                    sa.update(target)
                    .where(target.c.id == suggestion_id)
                    .values(data=new_val)
                )
                session.execute(upd)
                session.commit()
                return

            # Ensure concrete SQL types to avoid polymorphic unknown errors in to_jsonb
            status_json = sa.func.to_jsonb(sa.cast(sa.literal(status), sa.Text))
            moderator_json = sa.func.to_jsonb(sa.cast(sa.literal(moderator), sa.Text))
            note_json = sa.func.to_jsonb(sa.cast(sa.literal(note or ""), sa.Text))

            update_expr = sa.func.jsonb_set(
                sa.func.jsonb_set(
                    sa.func.jsonb_set(
                        target.c.payload,
                        "{moderation_status}",
                        status_json,
                        True,
                    ),
                    "{moderated_by}",
                    moderator_json,
                    True,
                ),
                "{moderation_note}",
                note_json,
                True,
            )
            if merged_id is not None:
                merged_id_json = sa.func.to_jsonb(
                    sa.cast(sa.literal(merged_id), sa.Integer)
                )
                update_expr = sa.func.jsonb_set(
                    update_expr,
                    "{merged_record_id}",
                    merged_id_json,
                    True,
                )
            stmt = (
                sa.update(target)
                .where(target.c.id == suggestion_id)
                .values(payload=update_expr)
            )
            session.execute(stmt)
            session.commit()

    # New: update the entire payload for a specific suggestion (used to persist edited fields)
    def update_payload(
        self, table: str, suggestion_id: int, payload: dict[str, Any]
    ) -> None:
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")
        with self.Session() as session:
            if table == "case_analyzer":
                import json as _json

                sel = (
                    sa.select(target.c.data)
                    .where(target.c.id == suggestion_id)
                    .limit(1)
                )
                row = session.execute(sel).first()
                current: dict[str, Any]
                if row and isinstance(row[0], dict):
                    current = dict(row[0])
                else:
                    try:
                        current = _json.loads(row[0]) if row else {}
                    except Exception:
                        current = {}
                merged = {**current, **payload}
                new_val = _json.dumps(self._to_jsonable(merged))
                upd = (
                    sa.update(target)
                    .where(target.c.id == suggestion_id)
                    .values(data=new_val)
                )
                session.execute(upd)
                session.commit()
                return

            stmt = (
                sa.update(target)
                .where(target.c.id == suggestion_id)
                .values(payload=self._to_jsonable(payload))
            )
            session.execute(stmt)
            session.commit()
