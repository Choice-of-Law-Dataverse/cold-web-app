import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
import jwt

from app.config import config


class SuggestionService:
    def __init__(self) -> None:
        # Prefer dedicated connection string for suggestions DB
        conn = config.SUGGESTIONS_SQL_CONN_STRING or config.SQL_CONN_STRING
        if not conn:
            raise RuntimeError("No SQL connection string configured for suggestions storage")

        self.engine = sa.create_engine(conn)
        self.schema = config.SUGGESTIONS_SCHEMA
        self.metadata = sa.MetaData(schema=self.schema)

        # Optionally ensure schema exists (if provided)
        if self.schema:
            with self.engine.connect() as conn_exec:
                conn_exec.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"'))
                conn_exec.commit()

        # Define the suggestions table (JSONB payload)
        self.table = sa.Table(
            config.SUGGESTIONS_TABLE or "user_suggestions",
            self.metadata,
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("payload", JSONB, nullable=False),
            sa.Column("client_ip", sa.String(64), nullable=True),
            sa.Column("user_agent", sa.Text, nullable=True),
            sa.Column("source", sa.String(256), nullable=True),
            sa.Column("token_sub", sa.String(256), nullable=True),
            extend_existing=True,
        )

        # Ensure table exists
        self.metadata.create_all(self.engine, tables=[self.table])
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def save_suggestion(
        self,
        payload: Dict[str, Any],
        *,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        source: Optional[str] = None,
        authorization: Optional[str] = None,
    ) -> int:
        token_sub: Optional[str] = None
        if authorization:
            try:
                parts = authorization.split()
                if len(parts) >= 2 and parts[0].lower() == "bearer":
                    decoded = jwt.decode(parts[1], config.JWT_SECRET, algorithms=["HS256"])  # type: ignore
                    token_sub = str(decoded.get("sub")) if isinstance(decoded, dict) else None
            except Exception:
                token_sub = None

        with self.Session() as session:
            stmt = self.table.insert().values(
                payload=payload,
                client_ip=client_ip,
                user_agent=user_agent,
                source=source,
                token_sub=token_sub,
            ).returning(self.table.c.id)
            result = session.execute(stmt)
            session.commit()
            new_id = result.scalar_one()
            return int(new_id)
