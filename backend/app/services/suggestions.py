import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa

from app.config import config
from app.services.db_manager import suggestions_db_manager
from app.services.suggestions_schema import SUGGESTION_TABLES, SUGGESTIONS_METADATA


class SuggestionService:
    """Stores suggestions in per-type Postgres tables using the default schema from the DSN."""

    def __init__(self) -> None:
        # Prefer dedicated connection string for suggestions DB
        conn = config.SUGGESTIONS_SQL_CONN_STRING or config.SQL_CONN_STRING
        if not conn:
            raise RuntimeError("No SQL connection string configured for suggestions storage")

        # Initialize the suggestions database manager if not already initialized
        if not suggestions_db_manager.is_initialized:
            suggestions_db_manager.initialize(conn)

        self.engine = suggestions_db_manager.get_engine()
        self.metadata = SUGGESTIONS_METADATA
        self.tables = SUGGESTION_TABLES

    def _get_token_sub(self, user: dict[str, Any] | None) -> str | None:
        """Extract email from Auth0 user payload and use as identifier."""
        if not user:
            return None
        # Auth0 custom claims with namespace
        return user.get("https://cold.global/email") or user.get("email") or user.get("sub")

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

    @staticmethod
    def _extract_moderation_status(payload: Any) -> str | None:
        if isinstance(payload, dict):
            status = payload.get("moderation_status")
            if isinstance(status, str):
                stripped = status.strip()
                return stripped or None
        return None

    def save_suggestion(
        self,
        payload: dict[str, Any],
        *,
        table: str = "generic",
        client_ip: str | None = None,
        user_agent: str | None = None,
        source: str | None = None,
        user: dict[str, Any] | None = None,
    ) -> int:
        token_sub = self._get_token_sub(user)
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")

        with suggestions_db_manager.get_session() as session:
            status_value = self._extract_moderation_status(payload)
            safe_payload = self._to_jsonable(payload)
            # Case analyzer table stores JSON in 'data' column
            if table == "case_analyzer":
                values: dict[str, Any] = {
                    "data": safe_payload,
                    "moderation_status": status_value,
                }
                if hasattr(target.c, "client_ip"):
                    values["client_ip"] = client_ip
                if hasattr(target.c, "user_agent"):
                    values["user_agent"] = user_agent
                if hasattr(target.c, "source"):
                    values["source"] = source
                if hasattr(target.c, "token_sub"):
                    values["token_sub"] = token_sub
                if hasattr(target.c, "user_email") and token_sub:
                    values["user_email"] = token_sub
                if hasattr(target.c, "username") and user and user.get("name"):
                    values["username"] = user.get("name")
                # Extract case_citation from nested structure if present
                if hasattr(target.c, "case_citation"):
                    case_citation_value = None
                    if isinstance(payload.get("case_citation"), dict):
                        case_citation_value = payload["case_citation"].get("case_citation")
                    elif isinstance(payload.get("case_citation"), str):
                        case_citation_value = payload["case_citation"]
                    values["case_citation"] = case_citation_value
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
                        moderation_status=status_value,
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
        with suggestions_db_manager.get_session() as session:
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
                def _optional_column(name: str) -> sa.Column | None:
                    col = getattr(target.c, name, None)
                    if col is None:
                        return None
                    cols.append(col)
                    return col

                username_col = _optional_column("username")
                user_email_col = _optional_column("user_email")
                model_col = _optional_column("model")
                citation_col = _optional_column("case_citation")
                source_col = _optional_column("source")
                query = sa.select(*cols)
                query = query.where(target.c.moderation_status.is_(None))
                if created_col is not None:
                    query = query.order_by(created_col.desc())
                query = query.limit(limit * 2)
                rows = session.execute(query).mappings().all()

                results: list[dict] = []

                for r in rows:
                    raw_data = r.get("data")
                    payload: Any
                    if isinstance(raw_data, dict):
                        payload = raw_data
                    else:
                        try:
                            payload = json.loads(raw_data) if raw_data is not None else {}
                        except Exception:
                            payload = {}
                    status = payload.get("moderation_status") if isinstance(payload, dict) else None
                    if status in {"approved", "rejected"}:
                        continue
                    results.append(
                        {
                            "id": r["id"],
                            "created_at": r.get("created_at"),
                            "payload": payload,
                            "source": r.get("source") if source_col is not None else None,
                            "username": r.get("username") if username_col is not None else None,
                            "user_email": r.get("user_email") if user_email_col is not None else None,
                            "model": r.get("model") if model_col is not None else None,
                            "case_citation": r.get("case_citation") if citation_col is not None else None,
                        }
                    )
                return results[:limit]

            # Default flow uses JSONB 'payload'
            pending_condition = sa.and_(
                target.c.moderation_status.is_(None),
                sa.or_(
                    ~target.c.payload.has_key("moderation_status"),  # type: ignore[attr-defined]
                    target.c.payload["moderation_status"].astext.is_(None),
                ),
            )
            query = (
                sa.select(
                    target.c.id,
                    target.c.created_at,
                    target.c.payload,
                    target.c.source,
                    target.c.token_sub,
                )
                .where(pending_condition)
                .order_by(target.c.created_at.desc())
                .limit(limit)
            )
            rows = session.execute(query).mappings().all()
            return [dict(r) for r in rows]

    def get_suggestion_by_id(
        self,
        table: str,
        suggestion_id: int,
        *,
        token_sub: str | None = None,
        pending_only: bool = False,
    ) -> dict | None:
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")

        with suggestions_db_manager.get_session() as session:
            if table == "case_analyzer":
                cols = [target.c.id]
                created_col = getattr(target.c, "created_at", None)
                if created_col is not None:
                    cols.append(created_col)
                data_col = getattr(target.c, "data", None)
                if data_col is None:
                    return None
                cols.append(data_col)

                def _optional_column(name: str) -> sa.Column | None:
                    col = getattr(target.c, name, None)
                    if col is None:
                        return None
                    cols.append(col)
                    return col

                username_col = _optional_column("username")
                user_email_col = _optional_column("user_email")
                model_col = _optional_column("model")
                citation_col = _optional_column("case_citation")
                source_col = _optional_column("source")
                status_col = _optional_column("moderation_status")
                submitted_data_col = _optional_column("submitted_data")

                query = sa.select(*cols).where(target.c.id == suggestion_id)
                if token_sub:
                    ownership_filters: list[Any] = []
                    if username_col is not None:
                        ownership_filters.append(username_col == token_sub)
                    if user_email_col is not None:
                        ownership_filters.append(user_email_col == token_sub)
                    if ownership_filters:
                        query = query.where(sa.or_(*ownership_filters))
                    else:
                        return None
                if pending_only:
                    # Support both old format (NULL = pending) and new format (status = 'pending')
                    query = query.where(
                        sa.or_(
                            target.c.moderation_status.is_(None),
                            target.c.moderation_status == "pending",
                        )
                    )
                row = session.execute(query).mappings().first()
                if not row:
                    return None

                # Parse data (legacy column - contains file info, full_text, etc.)
                raw_data = row.get("data")
                if isinstance(raw_data, dict):
                    legacy_data: Any = raw_data
                else:
                    try:
                        legacy_data = json.loads(raw_data) if raw_data is not None else {}
                    except Exception:
                        legacy_data = {}

                # Parse submitted_data (new column - contains user-edited analysis data)
                raw_submitted = row.get("submitted_data") if submitted_data_col is not None else None
                submitted_data: dict | None = None
                if raw_submitted is not None:
                    if isinstance(raw_submitted, dict):
                        submitted_data = raw_submitted
                    else:
                        try:
                            submitted_data = json.loads(raw_submitted)
                        except Exception:
                            submitted_data = None

                # Use submitted_data as payload if available (new format), otherwise legacy data
                payload: Any = submitted_data if submitted_data else legacy_data

                result = {
                    "id": row["id"],
                    "created_at": row.get("created_at"),
                    "payload": payload,
                    "data": legacy_data,  # Include legacy data for file_name, pdf_url access
                    "submitted_data": submitted_data,
                    "source": row.get("source") if source_col is not None else None,
                    "username": row.get("username") if username_col is not None else None,
                    "user_email": row.get("user_email") if user_email_col is not None else None,
                    "model": row.get("model") if model_col is not None else None,
                    "case_citation": row.get("case_citation") if citation_col is not None else None,
                    "moderation_status": row.get("moderation_status") if status_col is not None else None,
                }

                if pending_only:
                    status_val = result.get("moderation_status")
                    if status_val in {"approved", "rejected"}:
                        return None

                return result

            query = sa.select(
                target.c.id,
                target.c.created_at,
                target.c.payload,
                target.c.source,
                target.c.token_sub,
                target.c.moderation_status,
            ).where(target.c.id == suggestion_id)

            if token_sub:
                query = query.where(target.c.token_sub == token_sub)

            if pending_only:
                query = query.where(target.c.moderation_status.is_(None)).where(
                    sa.or_(
                        ~target.c.payload.has_key("moderation_status"),  # type: ignore[attr-defined]
                        target.c.payload["moderation_status"].astext.is_(None),
                    )
                )

            row = session.execute(query).mappings().first()
            if not row:
                return None

            payload_value = row.get("payload")
            if isinstance(payload_value, dict):
                payload_data: Any = payload_value
            else:
                try:
                    payload_data = json.loads(payload_value) if payload_value is not None else {}
                except Exception:
                    payload_data = {}

            return {
                "id": row["id"],
                "created_at": row.get("created_at"),
                "payload": payload_data,
                "source": row.get("source"),
                "token_sub": row.get("token_sub"),
                "moderation_status": row.get("moderation_status"),
            }

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
        with suggestions_db_manager.get_session() as session:
            if table == "case_analyzer":
                sel = sa.select(target.c.data).where(target.c.id == suggestion_id).limit(1)
                row = session.execute(sel).first()
                current: dict[str, Any]
                if row and isinstance(row[0], dict):
                    current = dict(row[0])
                else:
                    try:
                        current = json.loads(row[0]) if row else {}
                    except Exception:
                        current = {}
                current["moderation_status"] = status
                current["moderated_by"] = moderator
                current["moderation_note"] = note or ""
                if merged_id is not None:
                    current["merged_record_id"] = int(merged_id)
                json_ready = self._to_jsonable(current)
                upd = sa.update(target).where(target.c.id == suggestion_id).values(data=json_ready, moderation_status=status)
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
                merged_id_json = sa.func.to_jsonb(sa.cast(sa.literal(merged_id), sa.Integer))
                update_expr = sa.func.jsonb_set(
                    update_expr,
                    "{merged_record_id}",
                    merged_id_json,
                    True,
                )
            stmt = sa.update(target).where(target.c.id == suggestion_id).values(payload=update_expr, moderation_status=status)
            session.execute(stmt)
            session.commit()

    def get_case_analyzer_draft(self, draft_id: int) -> dict[str, Any] | None:
        """Get a case analyzer draft by ID. Returns the data payload or None if not found."""
        result = self.get_suggestion_by_id("case_analyzer", draft_id)
        if result is None:
            return None
        return result.get("payload", {})

    def update_case_analyzer_draft(self, draft_id: int, updates: dict[str, Any]) -> None:
        """Update a case analyzer draft by merging new fields into existing data."""
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            # Load existing data
            sel = sa.select(target.c.data).where(target.c.id == draft_id).limit(1)
            row = session.execute(sel).first()
            current: dict[str, Any]
            if row and isinstance(row[0], dict):
                current = dict(row[0])
            else:
                try:
                    current = json.loads(row[0]) if row else {}
                except Exception:
                    current = {}

            # Preserve critical fields if not explicitly being updated
            preserved_fields = ["pdf_url", "file_name", "full_text", "correlation_id"]
            for field in preserved_fields:
                if field in current and field not in updates:
                    updates[field] = current[field]

            # Merge updates into existing data
            merged = {**current, **updates}
            status_value = self._extract_moderation_status(merged)
            json_ready = self._to_jsonable(merged)

            # Update the record
            upd = sa.update(target).where(target.c.id == draft_id).values(data=json_ready, moderation_status=status_value)
            session.execute(upd)
            session.commit()

    # Generic update method for backward compatibility
    def update_payload(self, table: str, suggestion_id: int, payload: dict[str, Any]) -> None:
        target = self.tables.get(table)
        if target is None:
            raise ValueError(f"Unknown suggestions table '{table}'")
        with suggestions_db_manager.get_session() as session:
            if table == "case_analyzer":
                sel = sa.select(target.c.data).where(target.c.id == suggestion_id).limit(1)
                row = session.execute(sel).first()
                current: dict[str, Any]
                if row and isinstance(row[0], dict):
                    current = dict(row[0])
                else:
                    try:
                        current = json.loads(row[0]) if row else {}
                    except Exception:
                        current = {}
                merged = {**current, **payload}
                status_value = self._extract_moderation_status(merged)
                json_ready = self._to_jsonable(merged)
                upd = (
                    sa.update(target)
                    .where(target.c.id == suggestion_id)
                    .values(data=json_ready, moderation_status=status_value)
                )
                session.execute(upd)
                session.commit()
                return

            status_value = self._extract_moderation_status(payload)
            stmt = (
                sa.update(target)
                .where(target.c.id == suggestion_id)
                .values(payload=self._to_jsonable(payload), moderation_status=status_value)
            )
            session.execute(stmt)
            session.commit()

    # ========================================================================
    # New structured column methods for case_analyzer
    # ========================================================================

    def update_analyzer_step(
        self,
        draft_id: int,
        step_name: str,
        step_data: dict[str, Any],
    ) -> None:
        """
        Update a single step in the analyzer column.

        The analyzer column stores AI analysis steps with reasoning/confidence.
        Each step is stored as a key in the JSONB object.

        Args:
            draft_id: The case analyzer record ID
            step_name: Name of the step (e.g., 'jurisdiction', 'col_extraction')
            step_data: Step data including result, confidence, reasoning, etc.
        """
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            # Load existing analyzer data
            sel = sa.select(target.c.analyzer).where(target.c.id == draft_id).limit(1)
            row = session.execute(sel).first()

            current: dict[str, Any] = {}
            if row and row[0]:
                if isinstance(row[0], dict):
                    current = dict(row[0])
                else:
                    try:
                        current = json.loads(row[0])
                    except Exception:
                        current = {}

            # Add/update the step
            current[step_name] = self._to_jsonable(step_data)

            # Update the record
            upd = sa.update(target).where(target.c.id == draft_id).values(analyzer=current)
            session.execute(upd)
            session.commit()

    def get_analyzer_data(self, draft_id: int) -> dict[str, Any] | None:
        """
        Get the analyzer column data for a case analyzer record.

        Returns the analyzer JSONB data or None if not found.
        For backwards compatibility, returns empty dict if analyzer column is null.
        """
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            sel = sa.select(target.c.analyzer).where(target.c.id == draft_id).limit(1)
            row = session.execute(sel).first()

            if not row or row[0] is None:
                return {}

            if isinstance(row[0], dict):
                return dict(row[0])
            try:
                return json.loads(row[0])
            except Exception:
                return {}

    def set_submitted_data(
        self,
        draft_id: int,
        submitted_data: dict[str, Any],
    ) -> None:
        """
        Set the submitted_data column when user submits for approval.

        This also updates moderation_status to 'pending'.

        Args:
            draft_id: The case analyzer record ID
            submitted_data: The user-edited data submitted for moderation
        """
        target = self.tables["case_analyzer"]
        json_ready = self._to_jsonable(submitted_data)

        with suggestions_db_manager.get_session() as session:
            upd = (
                sa.update(target)
                .where(target.c.id == draft_id)
                .values(
                    submitted_data=json_ready,
                    moderation_status="pending",
                )
            )
            session.execute(upd)
            session.commit()

    def get_submitted_data(self, draft_id: int) -> dict[str, Any] | None:
        """
        Get the submitted_data column for a case analyzer record.

        Returns the submitted_data JSONB or None if not set.
        """
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            sel = sa.select(target.c.submitted_data).where(target.c.id == draft_id).limit(1)
            row = session.execute(sel).first()

            if not row or row[0] is None:
                return None

            if isinstance(row[0], dict):
                return dict(row[0])
            try:
                return json.loads(row[0])
            except Exception:
                return None

    def get_case_analyzer_full(self, draft_id: int) -> dict[str, Any] | None:
        """
        Get complete case analyzer record with all columns.

        Returns a dict with:
        - id, created_at, username, user_email, model, case_citation
        - data: legacy data column (for backwards compat)
        - analyzer: AI analysis steps
        - submitted_data: user-submitted data for approval
        - moderation_status: current status
        """
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            query = sa.select(
                target.c.id,
                target.c.created_at,
                target.c.username,
                target.c.user_email,
                target.c.model,
                target.c.case_citation,
                target.c.data,
                target.c.analyzer,
                target.c.submitted_data,
                target.c.moderation_status,
            ).where(target.c.id == draft_id)

            row = session.execute(query).mappings().first()
            if not row:
                return None

            def _parse_json(val: Any) -> dict[str, Any] | None:
                if val is None:
                    return None
                if isinstance(val, dict):
                    return dict(val)
                try:
                    return json.loads(val)
                except Exception:
                    return None

            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "username": row["username"],
                "user_email": row["user_email"],
                "model": row["model"],
                "case_citation": row["case_citation"],
                "data": _parse_json(row["data"]) or {},
                "analyzer": _parse_json(row["analyzer"]) or {},
                "submitted_data": _parse_json(row["submitted_data"]),
                "moderation_status": row["moderation_status"],
            }

    def get_display_data_for_moderation(self, draft_id: int) -> dict[str, Any] | None:
        """
        Get the data to display for moderation with backwards compatibility.

        Priority:
        1. submitted_data (new records with user submissions)
        2. data column (legacy records)

        Returns None if record not found.
        """
        record = self.get_case_analyzer_full(draft_id)
        if not record:
            return None

        # Prefer submitted_data if available
        if record.get("submitted_data"):
            return record["submitted_data"]

        # Fall back to legacy data column
        return record.get("data", {})

    def list_pending_case_analyzer(self, limit: int = 100) -> list[dict]:
        """
        List case analyzer records pending moderation.

        Uses moderation_status column as source of truth.
        Returns records where status is 'pending'.
        """
        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            query = (
                sa.select(
                    target.c.id,
                    target.c.created_at,
                    target.c.username,
                    target.c.user_email,
                    target.c.model,
                    target.c.case_citation,
                    target.c.data,
                    target.c.analyzer,
                    target.c.submitted_data,
                    target.c.moderation_status,
                )
                .where(target.c.moderation_status == "pending")
                .order_by(target.c.created_at.desc())
                .limit(limit)
            )

            rows = session.execute(query).mappings().all()

            def _parse_json(val: Any) -> dict[str, Any] | None:
                if val is None:
                    return None
                if isinstance(val, dict):
                    return dict(val)
                try:
                    return json.loads(val)
                except Exception:
                    return None

            results: list[dict] = []
            for r in rows:
                submitted = _parse_json(r["submitted_data"])
                legacy_data = _parse_json(r["data"]) or {}

                # Use submitted_data if available, else legacy
                display_data = submitted if submitted else legacy_data

                results.append(
                    {
                        "id": r["id"],
                        "created_at": r["created_at"],
                        "username": r["username"],
                        "user_email": r["user_email"],
                        "model": r["model"],
                        "case_citation": r["case_citation"],
                        "payload": display_data,
                        "data": legacy_data,  # Include original data for pdf_url, file_name
                        "submitted_data": submitted,
                        "analyzer": _parse_json(r["analyzer"]) or {},
                        "moderation_status": r["moderation_status"],
                    }
                )

            return results

    def update_moderation_status(
        self,
        draft_id: int,
        status: str,
    ) -> None:
        """
        Update just the moderation_status column.

        Valid statuses: 'draft', 'analyzing', 'completed', 'pending', 'approved', 'rejected', 'failed'
        """
        valid_statuses = {"draft", "analyzing", "completed", "pending", "approved", "rejected", "failed"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

        target = self.tables["case_analyzer"]
        with suggestions_db_manager.get_session() as session:
            upd = sa.update(target).where(target.c.id == draft_id).values(moderation_status=status)
            session.execute(upd)
            session.commit()
