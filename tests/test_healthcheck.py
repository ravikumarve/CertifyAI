"""Healthcheck command — orchestration signal tests (no LLM calls)."""

from click.testing import CliRunner

from certifyai.cli.main import cli


def test_healthcheck_fresh_dir_warns_not_fails(tmp_path, monkeypatch):
    """Fresh dir: missing vault = warning, temp DB initializes cleanly."""
    monkeypatch.delenv("CERTIFYAI_API_KEY", raising=False)
    runner = CliRunner()
    db = str(tmp_path / "sub" / "health.db")
    result = runner.invoke(cli, ["healthcheck", "--db", db, "--vault", str(tmp_path / "vault")])
    assert result.exit_code == 0, result.output
    assert "healthy" in result.output


def test_healthcheck_reports_schema_version(tmp_path, monkeypatch):
    """Schema version line matches models.SCHEMA_VERSION."""
    from certifyai.engine.database.models import SCHEMA_VERSION

    monkeypatch.delenv("CERTIFYAI_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["healthcheck", "--db", str(tmp_path / "h.db")])
    assert result.exit_code == 0, result.output
    assert f"schema v{SCHEMA_VERSION}" in result.output
