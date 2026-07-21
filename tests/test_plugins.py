"""Tests for the plugin system — registry, discovery, external plugins."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from certifyai.engine.models import AttackCategory, AttackScenario
from certifyai.engine.registry import PluginRegistry
from certifyai.engine.redteam.base import AttackPlugin


class TestPluginRegistry:
    """Tests for the core plugin registry."""

    def test_load_all_plugins(self) -> None:
        registry = PluginRegistry()
        registry.load_all()
        plugins = registry.plugins
        assert len(plugins) > 0
        # Should have all 6 categories after we added the 3 new ones
        assert AttackCategory.PROMPT_INJECTION in plugins
        assert AttackCategory.JAILBREAK in plugins
        assert AttackCategory.PII_LEAKAGE in plugins
        assert AttackCategory.POLICY_VIOLATION in plugins
        assert AttackCategory.HALLUCINATION in plugins
        assert AttackCategory.BIAS in plugins

    def test_scenarios_count(self) -> None:
        registry = PluginRegistry()
        scenarios = registry.scenarios
        assert len(scenarios) >= 18  # 6 categories × 3 scenarios each minimum

    def test_get_scenarios_by_category_all(self) -> None:
        registry = PluginRegistry()
        all_scenarios = registry.get_scenarios_by_category(None)
        assert len(all_scenarios) == len(registry.scenarios)

    def test_get_scenarios_by_category_filter(self) -> None:
        registry = PluginRegistry()
        injection = registry.get_scenarios_by_category(
            [AttackCategory.PROMPT_INJECTION]
        )
        assert len(injection) >= 3
        for s in injection:
            assert s.category == AttackCategory.PROMPT_INJECTION

    def test_get_plugin(self) -> None:
        registry = PluginRegistry()
        plugin = registry.get_plugin(AttackCategory.PROMPT_INJECTION)
        assert isinstance(plugin, AttackPlugin)
        assert plugin.category == AttackCategory.PROMPT_INJECTION

    def test_get_plugin_not_found(self) -> None:
        """Getting a plugin for a category with no registered handler raises KeyError."""
        # Create a custom registry subclass that doesn't register any plugins
        class EmptyRegistry(PluginRegistry):
            def _load_builtin_plugins(self) -> None:
                pass  # skip all built-in plugins

        registry = EmptyRegistry()
        with pytest.raises(KeyError):
            registry.get_plugin(AttackCategory.PROMPT_INJECTION)

    def test_list_categories(self) -> None:
        registry = PluginRegistry()
        cats = registry.list_categories()
        assert len(cats) == 6
        assert all(isinstance(c, AttackCategory) for c in cats)

    def test_reload(self) -> None:
        registry = PluginRegistry()
        registry.load_all()
        count_before = len(registry.scenarios)
        registry.reload()
        count_after = len(registry.scenarios)
        assert count_before == count_after

    def test_lazy_loading(self) -> None:
        """Registry should auto-load on first property access."""
        registry = PluginRegistry()
        assert not registry._loaded
        _ = registry.plugins  # triggers load
        assert registry._loaded


class TestExternalPlugins:
    """Tests for loading external user-defined plugins."""

    @pytest.fixture
    def external_plugin_dir(self) -> Path:
        """Create a temporary directory with a custom attack plugin."""
        tmpdir = Path(tempfile.mkdtemp())

        plugin_code = '''
from __future__ import annotations

from typing import Any

from certifyai.engine.models import AttackCategory, AttackScenario, Severity
from certifyai.engine.redteam.base import AttackPlugin


class CustomExternalPlugin(AttackPlugin):
    """A user-defined plugin from an external directory."""

    @property
    def category(self) -> AttackCategory:
        return AttackCategory.PROMPT_INJECTION  # same category as built-in

    def get_scenarios(self) -> list[AttackScenario]:
        return [
            AttackScenario(
                id="EXTERNAL-001",
                name="Custom External Attack",
                category=self.category,
                severity=Severity.HIGH,
                description="An external plugin scenario.",
                prompts=["Test prompt"],
                pass_criteria={"forbidden_phrases": ["compromised"]},
                clause_refs=[],
                tags=["external", "test"],
            ),
        ]

    async def evaluate(
        self, scenario: AttackScenario, prompt: str, response: str
    ) -> dict[str, Any]:
        return {"passed": True, "external_eval": True}
'''
        plugin_file = tmpdir / "my_custom_plugin.py"
        plugin_file.write_text(plugin_code, encoding="utf-8")
        return tmpdir

    def test_load_external_plugin(self, external_plugin_dir: Path) -> None:
        registry = PluginRegistry(plugin_dirs=[external_plugin_dir])
        registry.load_all()

        # Should have the external scenario
        scenarios = registry.scenarios
        external_ids = [s.id for s in scenarios if s.id == "EXTERNAL-001"]
        assert len(external_ids) == 1

    def test_external_overrides_builtin(self, external_plugin_dir: Path) -> None:
        """External plugins with the same category should add scenarios
        (not override — we append scenarios from all plugins)."""
        registry = PluginRegistry(plugin_dirs=[external_plugin_dir])
        registry.load_all()

        # The external plugin's scenario should be present alongside built-in ones
        injection_scenarios = registry.get_scenarios_by_category(
            [AttackCategory.PROMPT_INJECTION]
        )
        ids = [s.id for s in injection_scenarios]
        assert "EXTERNAL-001" in ids
        assert "INJECTION-001" in ids  # built-in still present

    def test_multiple_external_dirs(self) -> None:
        """Load plugins from multiple external directories."""
        tmpdir1 = Path(tempfile.mkdtemp())
        tmpdir2 = Path(tempfile.mkdtemp())

        plugin1 = '''
from __future__ import annotations
from typing import Any
from certifyai.engine.models import AttackCategory, AttackScenario, Severity
from certifyai.engine.redteam.base import AttackPlugin

class PluginA(AttackPlugin):
    @property
    def category(self) -> AttackCategory:
        return AttackCategory.POLICY_VIOLATION
    def get_scenarios(self) -> list[AttackScenario]:
        return [AttackScenario(id="PLUGIN-A", name="Plugin A", category=self.category, severity=Severity.LOW, description="Test", prompts=["p"], pass_criteria={}, clause_refs=[], tags=[])]
    async def evaluate(self, scenario, prompt, response) -> dict[str, Any]:
        return {"passed": True}
'''
        plugin2 = '''
from __future__ import annotations
from typing import Any
from certifyai.engine.models import AttackCategory, AttackScenario, Severity
from certifyai.engine.redteam.base import AttackPlugin

class PluginB(AttackPlugin):
    @property
    def category(self) -> AttackCategory:
        return AttackCategory.BIAS
    def get_scenarios(self) -> list[AttackScenario]:
        return [AttackScenario(id="PLUGIN-B", name="Plugin B", category=self.category, severity=Severity.LOW, description="Test", prompts=["p"], pass_criteria={}, clause_refs=[], tags=[])]
    async def evaluate(self, scenario, prompt, response) -> dict[str, Any]:
        return {"passed": True}
'''
        (tmpdir1 / "plugin_a.py").write_text(plugin1, encoding="utf-8")
        (tmpdir2 / "plugin_b.py").write_text(plugin2, encoding="utf-8")

        registry = PluginRegistry(plugin_dirs=[tmpdir1, tmpdir2])
        registry.load_all()

        ids = [s.id for s in registry.scenarios]
        assert "PLUGIN-A" in ids
        assert "PLUGIN-B" in ids

    def test_external_plugin_error_handling(self) -> None:
        """Invalid plugin files should not crash the registry."""
        tmpdir = Path(tempfile.mkdtemp())
        bad_plugin = tmpdir / "bad_plugin.py"
        bad_plugin.write_text(
            "this is not valid python ====", encoding="utf-8"
        )

        # Should not raise — just log the error
        registry = PluginRegistry(plugin_dirs=[tmpdir])
        registry.load_all()  # Should not crash

    def test_nonexistent_plugin_dir(self) -> None:
        """Non-existent plugin directories should be silently ignored."""
        registry = PluginRegistry(
            plugin_dirs=[Path("/tmp/nonexistent_plugin_dir_xyz")]
        )
        registry.load_all()  # Should not raise
        assert len(registry.scenarios) >= 18  # Should still have built-in


class TestPluginScenarioIntegrity:
    """Verify that every plugin produces valid scenarios."""

    def test_all_scenarios_have_unique_ids(self) -> None:
        registry = PluginRegistry()
        ids = [s.id for s in registry.scenarios]
        assert len(ids) == len(set(ids)), (
            f"Duplicate scenario IDs found: "
            f"{[id for id in ids if ids.count(id) > 1]}"
        )

    def test_all_scenarios_have_valid_categories(self) -> None:
        registry = PluginRegistry()
        valid_categories = set(AttackCategory)
        for s in registry.scenarios:
            assert s.category in valid_categories, (
                f"Scenario {s.id} has invalid category {s.category}"
            )

    def test_all_scenarios_have_at_least_one_prompt(self) -> None:
        registry = PluginRegistry()
        for s in registry.scenarios:
            assert len(s.prompts) >= 1, (
                f"Scenario {s.id} has no prompts"
            )

    def test_all_scenarios_have_pass_criteria(self) -> None:
        registry = PluginRegistry()
        for s in registry.scenarios:
            assert len(s.pass_criteria) >= 1, (
                f"Scenario {s.id} has no pass criteria"
            )

    def test_all_scenarios_have_clause_refs(self) -> None:
        registry = PluginRegistry()
        for s in registry.scenarios:
            assert len(s.clause_refs) >= 1, (
                f"Scenario {s.id} has no regulatory clause references"
            )

    def test_all_scenarios_have_tags(self) -> None:
        registry = PluginRegistry()
        for s in registry.scenarios:
            assert len(s.tags) >= 1, (
                f"Scenario {s.id} has no tags"
            )

    def test_all_scenarios_have_correct_id_format(self) -> None:
        """IDs should be of the form CATEGORY-NNN."""
        import re

        registry = PluginRegistry()
        for s in registry.scenarios:
            category_prefix = s.category.name.split("_")[0][:4].upper()
            assert re.match(r"^[A-Z]+-\d{3}$", s.id), (
                f"Scenario {s.id} does not match ID format CATEGORY-NNN"
            )
