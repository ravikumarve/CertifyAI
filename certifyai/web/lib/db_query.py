#!/usr/bin/env python3
"""Read CertifyAI SQLite database and output JSON for the web dashboard.

Called as a subprocess by the Next.js API route. Usage:
    python3 db_query.py <db_path> <mode>
    Modes: dashboard, runs, config

Outputs JSON to stdout. Errors to stderr.
"""

import json
import os
import sqlite3
import sys
from pathlib import Path


def get_db_path() -> str:
    if len(sys.argv) > 1 and sys.argv[1] != "--":
        return sys.argv[1]
    here = Path(__file__).resolve().parent
    for p in [here / "../../../../certifyai.db", here / "../../../certifyai.db"]:
        if p.exists():
            return str(p.resolve())
    return "certifyai.db"


def get_mode() -> str:
    return sys.argv[2] if len(sys.argv) > 2 else "dashboard"


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def query(db_path: str, mode: str) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()

    if mode == "dashboard":
        return _dashboard(cursor)
    elif mode == "runs":
        return _runs(cursor)
    elif mode == "config":
        return _config(cursor)
    return {"error": f"Unknown mode: {mode}"}


def _parse_config_json(config_json: str | None) -> dict:
    if not config_json:
        return {}
    try:
        return json.loads(config_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def _dashboard(cursor) -> dict:
    cursor.execute(
        "SELECT id, status, started_at, finished_at, config_json, "
        "total_attacks, passed, failed, errors, skipped, overall_score, "
        "engine_version, created_at "
        "FROM runs ORDER BY created_at DESC LIMIT 1"
    )
    latest = cursor.fetchone()

    cfg = _parse_config_json(latest["config_json"] if latest else None)
    provider_info = cfg.get("provider", {})
    provider_name = provider_info.get("provider", "—")
    model_name = provider_info.get("model", "—")
    frameworks_list = cfg.get("frameworks", [])
    concurrency_val = cfg.get("concurrency", 3)

    recent_results = []
    if latest:
        cursor.execute(
            "SELECT id, run_id, scenario_id, attack_name, category, severity, "
            "status, response_time_ms, evaluation "
            "FROM results WHERE run_id = ? ORDER BY id LIMIT 50",
            (latest["id"],),
        )
        recent_results = cursor.fetchall()

    cursor.execute(
        "SELECT id, run_id, previous_hash, run_hash, timestamp, metadata, verified_at "
        "FROM evidence_chain ORDER BY timestamp DESC LIMIT 50"
    )
    vault_entries = cursor.fetchall()

    cursor.execute(
        "SELECT COALESCE(SUM(passed), 0) as total_passed, "
        "COALESCE(SUM(failed), 0) as total_failed, "
        "COALESCE(SUM(errors), 0) as total_errors, "
        "COALESCE(SUM(total_attacks), 0) as total_attacks "
        "FROM runs"
    )
    aggr = cursor.fetchone()

    current_run = None
    if latest and latest["status"] in ("running", "pending"):
        current_run = {
            "id": latest["id"],
            "provider": provider_name,
            "model": model_name,
            "frameworks": frameworks_list,
            "concurrency": concurrency_val,
            "status": latest["status"],
        }

    conn = cursor.connection
    conn.close()

    elapsed = 0
    if latest:
        if latest["finished_at"]:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(latest["started_at"])
                end = datetime.fromisoformat(latest["finished_at"])
                elapsed = int((end - start).total_seconds())
            except (ValueError, TypeError):
                elapsed = 0
        elif latest["started_at"]:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(latest["started_at"])
                elapsed = int((datetime.now() - start).total_seconds())
            except (ValueError, TypeError):
                elapsed = 0

    return {
        "stats": {
            "score": round(latest["overall_score"] * 100, 1) if latest and latest["overall_score"] is not None else None,
            "passed": aggr["total_passed"] if aggr else 0,
            "failed": aggr["total_failed"] if aggr else 0,
            "total": aggr["total_attacks"] if aggr else 0,
            "running_time_secs": elapsed,
            "last_run_id": latest["id"] if latest else None,
            "provider": provider_name,
            "model": model_name,
            "frameworks": frameworks_list,
            "engine_status": "ONLINE",
            "vault_status": "LOCKED" if vault_entries else "EMPTY",
            "version": latest["engine_version"] if latest else "v0.1.0",
        },
        "current_run": current_run,
        "recent_results": recent_results,
        "vault_log": vault_entries,
    }


def _runs(cursor) -> dict:
    cursor.execute(
        "SELECT id, status, passed, failed, errors, skipped, total_attacks, "
        "overall_score, config_json, engine_version, created_at "
        "FROM runs ORDER BY created_at DESC LIMIT 100"
    )
    runs_data = cursor.fetchall()
    for r in runs_data:
        cfg = _parse_config_json(r.get("config_json"))
        prov = cfg.get("provider", {})
        r["provider"] = prov.get("provider", "—")
        r["model"] = prov.get("model", "—")
        r["score"] = r.pop("overall_score", None)
        r["total"] = r.pop("total_attacks", 0)
        # Also scale score for display
        if r["score"] is not None:
            r["score"] = round(r["score"] * 100, 1)
    conn = cursor.connection
    conn.close()
    return {"runs": runs_data}


def _config(cursor) -> dict:
    cursor.execute("SELECT key, value, category, description FROM config ORDER BY category, key")
    rows = cursor.fetchall()
    if rows:
        config_from_db = {}
        for r in rows:
            cat = r["category"]
            if cat not in config_from_db:
                config_from_db[cat] = {}
            config_from_db[cat][r["key"]] = r["value"]
        return {"config": config_from_db, "source": "db"}

    cursor.execute(
        "SELECT config_json FROM runs ORDER BY created_at DESC LIMIT 1"
    )
    latest_run = cursor.fetchone()
    if latest_run and latest_run.get("config_json"):
        cfg = _parse_config_json(latest_run["config_json"])
        return {"config": cfg, "source": "run_config"}

    return {"config": {}, "source": "none"}


if __name__ == "__main__":
    db_path = get_db_path()
    mode = get_mode()

    if not os.path.exists(db_path):
        print(json.dumps({"error": f"Database not found: {db_path}"}))
        sys.exit(1)

    try:
        data = query(db_path, mode)
        print(json.dumps(data, default=str, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
