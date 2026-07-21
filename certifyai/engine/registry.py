"""Plugin registry — discovers and manages attack scenario plugins."""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from certifyai.engine.models import AttackCategory, AttackScenario
from certifyai.engine.redteam.base import AttackPlugin


class PluginRegistry:
    """Discovers and provides access to attack plugins.

    Plugins are auto-discovered from the redteam package by scanning for
    subclasses of AttackPlugin.
    """

    def __init__(self) -> None:
        self._plugins: dict[AttackCategory, AttackPlugin] = {}
        self._scenarios: list[AttackScenario] = []
        self._loaded = False

    def load_all(self) -> None:
        """Discover and load all attack plugins from the redteam package."""
        if self._loaded:
            return

        import certifyai.engine.redteam as redteam_pkg

        for _importer, modname, ispkg in pkgutil.walk_packages(
            redteam_pkg.__path__, prefix=f"{redteam_pkg.__name__}."
        ):
            if ispkg or modname.endswith(".base"):
                continue

            try:
                module = importlib.import_module(modname)
            except ImportError:
                continue

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, AttackPlugin)
                    and obj is not AttackPlugin
                    and not inspect.isabstract(obj)
                ):
                    plugin = obj()
                    self._plugins[plugin.category] = plugin
                    self._scenarios.extend(plugin.get_scenarios())

        self._loaded = True

    @property
    def plugins(self) -> dict[AttackCategory, AttackPlugin]:
        """All loaded plugins, keyed by category."""
        if not self._loaded:
            self.load_all()
        return dict(self._plugins)

    @property
    def scenarios(self) -> list[AttackScenario]:
        """All discovered attack scenarios."""
        if not self._loaded:
            self.load_all()
        return list(self._scenarios)

    def get_scenarios_by_category(
        self, categories: list[AttackCategory] | None = None
    ) -> list[AttackScenario]:
        """Get scenarios filtered by category.

        Args:
            categories: Categories to include. None = all categories.

        Returns:
            Filtered list of scenarios.
        """
        if categories is None:
            return self.scenarios
        return [s for s in self.scenarios if s.category in categories]

    def get_plugin(self, category: AttackCategory) -> AttackPlugin:
        """Get the plugin for a specific category."""
        plugins = self.plugins
        if category not in plugins:
            raise KeyError(f"No plugin registered for category: {category}")
        return plugins[category]
