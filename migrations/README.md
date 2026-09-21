# Migrations — SQLite schema versioning

CertifyAI is local-first SQLite (WAL mode). There is no Alembic server
round-trip; versioning is file-based and enforced at connect time:

- `001_initial_schema.sql` — fresh-install baseline. Mirrors
  `certifyai/engine/database/models.py` (`SCHEMA_VERSION = 1`) and
  `CREATE_TRIGGERS_SQL`. Applied automatically by `DatabaseManager`
  via `Base.metadata.create_all` on first connect.
- Every applied version is recorded in the `_schema_version` table
  (`version`, `applied_at`, `script_name`). `DatabaseManager.initialize()`
  seeds version 1 when the table is empty.
- **Rule for contributors:** schema changes ship as `002_<name>.sql`,
  `003_<name>.sql`, … and bump `SCHEMA_VERSION` in `models.py`.
  Never edit `001` after release — buyers' vaults depend on the chain.
- **Check your DB:** `certifyai healthcheck --db <path>` reports the
  recorded schema version alongside vault integrity.
