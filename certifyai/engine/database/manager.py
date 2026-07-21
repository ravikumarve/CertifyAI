"""DatabaseManager — async SQLite connection, WAL mode, schema init, migrations.

Usage::

    from certifyai.engine.database.manager import DatabaseManager

    async with DatabaseManager("certifyai.db") as db:
        # db.run_session(...) for write operations
        # db.read_session(...) for read-only operations
        run = await db.get_run("run_abc123")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from certifyai.engine.database.models import (
    CREATE_TRIGGERS_SQL,
    SCHEMA_VERSION,
    Base,
    ConfigRecord,
    EvidenceChainRecord,
    ResultRecord,
    RunRecord,
)

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = "certifyai.db"


class DatabaseManager:
    """Manages the SQLite database lifecycle.

    - Creates async engine with aiosqlite
    - Enables WAL mode for concurrent reads
    - Initializes schema and runs migrations on first connect
    - Provides session factories for read and write operations
    """

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path).resolve()
        self._engine: Any = None
        self._async_session_maker: async_sessionmaker[AsyncSession] | None = None
        self._read_session_maker: async_sessionmaker[AsyncSession] | None = None
        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> DatabaseManager:
        await self.initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def initialize(self) -> None:
        """Create engine, init schema, run migrations."""
        if self._initialized:
            return

        db_url = f"sqlite+aiosqlite:///{self.db_path}"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_async_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )

        # Create session factories
        self._async_session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._read_session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Init schema
        async with self._engine.begin() as conn:
            await self._init_schema(conn)

        self._initialized = True
        logger.info("Database initialized: %s", self.db_path)

    async def close(self) -> None:
        """Dispose of the engine and release resources."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
        self._initialized = False
        logger.debug("Database closed: %s", self.db_path)

    @property
    def is_initialized(self) -> bool:
        """Whether the database engine and schema have been initialized."""
        return self._initialized

    # ------------------------------------------------------------------
    # Session access
    # ------------------------------------------------------------------

    def session(self) -> AsyncSession:
        """Get a new async session for read/write operations."""
        if self._async_session_maker is None:
            raise RuntimeError("DatabaseManager not initialized. Call initialize() first.")
        return self._async_session_maker()

    def read_session(self) -> AsyncSession:
        """Get a new async session for read-only operations."""
        if self._read_session_maker is None:
            raise RuntimeError("DatabaseManager not initialized. Call initialize() first.")
        return self._read_session_maker()

    # ------------------------------------------------------------------
    # Schema init & migrations
    # ------------------------------------------------------------------

    async def _init_schema(self, conn: AsyncConnection) -> None:
        """Create tables + triggers if they don't exist yet."""
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable WAL mode, foreign keys, and set up triggers
        for stmt in CREATE_TRIGGERS_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                try:
                    await conn.execute(text(stmt + ";"))
                except Exception:
                    logger.debug("Trigger/Pragma already exists (safe to ignore)")

        # Seed schema version if empty
        result = await conn.execute(text("SELECT COUNT(*) FROM _schema_version"))
        count = result.scalar()
        if count == 0:
            from datetime import UTC, datetime

            now = datetime.now(UTC).isoformat()
            await conn.execute(
                text(
                    "INSERT INTO _schema_version (version, applied_at, script_name) "
                    "VALUES (:v, :a, :n)"
                ),
                {"v": SCHEMA_VERSION, "a": now, "n": "initial_schema"},
            )

        logger.debug("Schema initialized at version %d", SCHEMA_VERSION)

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    async def save_run(self, run: RunRecord) -> None:
        """Insert or update a run record."""
        async with self.session() as s:
            await s.merge(run)
            await s.commit()

    async def get_run(self, run_id: str) -> RunRecord | None:
        """Get a run by ID."""
        async with self.read_session() as s:
            return await s.get(RunRecord, run_id)

    async def list_runs(self, limit: int = 20, offset: int = 0) -> list[RunRecord]:
        """List recent runs ordered by start time descending."""
        async with self.read_session() as s:
            from sqlalchemy import select

            stmt = (
                select(RunRecord).order_by(RunRecord.started_at.desc()).limit(limit).offset(offset)
            )
            result = await s.execute(stmt)
            return list(result.scalars().all())

    async def save_result(self, result: ResultRecord) -> None:
        """Insert or update a result record."""
        async with self.session() as s:
            await s.merge(result)
            await s.commit()

    async def save_results(self, results: list[ResultRecord]) -> None:
        """Bulk insert results in a single transaction."""
        if not results:
            return
        async with self.session() as s:
            for r in results:
                await s.merge(r)
            await s.commit()

    async def get_results_by_run(self, run_id: str) -> list[ResultRecord]:
        """Get all results for a given run."""
        async with self.read_session() as s:
            from sqlalchemy import select

            stmt = (
                select(ResultRecord)
                .where(ResultRecord.run_id == run_id)
                .order_by(ResultRecord.started_at)
            )
            result = await s.execute(stmt)
            return list(result.scalars().all())

    async def save_evidence_chain(self, chain: EvidenceChainRecord) -> None:
        """Insert an evidence chain entry."""
        async with self.session() as s:
            s.add(chain)
            await s.commit()

    async def get_latest_chain_entry(
        self,
    ) -> EvidenceChainRecord | None:
        """Get the most recent evidence chain entry (to read previous_hash)."""
        async with self.read_session() as s:
            from sqlalchemy import select

            stmt = select(EvidenceChainRecord).order_by(EvidenceChainRecord.id.desc()).limit(1)
            result = await s.execute(stmt)
            return result.scalar_one_or_none()

    async def get_config(self, key: str) -> str | None:
        """Get a config value by key."""
        async with self.read_session() as s:
            record = await s.get(ConfigRecord, key)
            return record.value if record else None

    async def set_config(
        self, key: str, value: str, category: str = "general", description: str | None = None
    ) -> None:
        """Set a config value."""
        async with self.session() as s:
            record = ConfigRecord(
                key=key,
                value=value,
                category=category,
                description=description,
            )
            await s.merge(record)
            await s.commit()

    # ------------------------------------------------------------------
    # Aggregation queries
    # ------------------------------------------------------------------

    async def get_run_summary_stats(self) -> dict[str, Any]:
        """Get aggregate statistics across all runs."""
        async with self.read_session() as s:
            from sqlalchemy import func, select

            # Total runs
            total_runs_result = await s.execute(select(func.count(RunRecord.id)))
            total_runs = total_runs_result.scalar() or 0

            # Aggregated attack counts
            agg_result = await s.execute(
                select(
                    func.sum(RunRecord.total_attacks),
                    func.sum(RunRecord.passed),
                    func.sum(RunRecord.failed),
                    func.sum(RunRecord.errors),
                )
            )
            row = agg_result.one()
            return {
                "total_runs": total_runs,
                "total_attacks": row[0] or 0,
                "total_passed": row[1] or 0,
                "total_failed": row[2] or 0,
                "total_errors": row[3] or 0,
            }

    async def get_results_by_category(self, run_id: str) -> list[dict[str, Any]]:
        """Get per-category pass/fail counts for a run."""
        async with self.read_session() as s:
            from sqlalchemy import func, select

            stmt = (
                select(
                    ResultRecord.category,
                    ResultRecord.status,
                    func.count(ResultRecord.id),
                )
                .where(ResultRecord.run_id == run_id)
                .group_by(ResultRecord.category, ResultRecord.status)
            )
            result = await s.execute(stmt)
            return [{"category": row[0], "status": row[1], "count": row[2]} for row in result.all()]
