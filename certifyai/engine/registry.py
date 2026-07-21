"""Plugin registry — discovers and manages attack scenario plugins.

Supports auto-discovery of built-in plugins from the certifyai.engine.redteam
package AND loading of external user-defined plugins from custom directories.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Any

from certifyai.engine.models import AttackCategory, AttackScenario
from certifyai.engine.redteam.base import AttackPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Discovers and provides access to attack plugins.

    Plugins are auto-discovered from two sources:
    1. The built-in ``redteam`` package (certifyai.engine.redteam)
    2. Optional external directories specified via ``plugin_dirs``

    External plugins are Python files in the given directories that contain
    subclasses of ``AttackPlugin``. They take precedence over built-in plugins
    when they define the same category.
    """

    def __init__(self, plugin_dirs: list[Path] | None = None) -> None:
        self._plugins: dict[AttackCategory, AttackPlugin] = {}
        self._scenarios: list[AttackScenario] = []
        self._loaded = False
        self._plugin_dirs: list[Path] = [
            p.resolve() for p in (plugin_dirs or []) if p.exists()
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

    def load_all(self) -> None:
        """Discover and load all attack plugins.

        Loads built-in plugins first, then external plugins. External
        plugins override built-in ones when they share a category.
        """
        if self._loaded:
            return
        self._load_builtin_plugins()
        self._load_external_plugins()
        self._loaded = True

    def get_scenarios_by_category(
        self, categories: list[AttackCategory] | None = None
    ) -> list[AttackScenario]:
        """Get scenarios filtered by category.

        Args:
            categories: Categories to include. ``None`` = all categories.

        Returns:
            Filtered list of scenarios.
        """
        if categories is None:
            return self.scenarios
        return [s for s in self.scenarios if s.category in categories]

    def get_plugin(self, category: AttackCategory) -> AttackPlugin:
        """Get the plugin for a specific category.

        Raises:
            KeyError: If no plugin is registered for the given category.
        """
        plugins = self.plugins
        if category not in plugins:
            raise KeyError(f"No plugin registered for category: {category}")
        return plugins[category]

    def list_categories(self) -> list[AttackCategory]:
        """List all registered attack categories."""
        return sorted(self.plugins.keys(), key=lambda c: c.value)

    def reload(self) -> None:
        """Force a full reload of all plugins."""
        self._plugins.clear()
        self._scenarios.clear()
        self._loaded = False
        self.load_all()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_builtin_plugins(self) -> None:
        """Scan the built-in redteam package for AttackPlugin subclasses."""
        import certifyai.engine.redteam as redteam_pkg

        for _importer, modname, ispkg in pkgutil.walk_packages(
            redteam_pkg.__path__, prefix=f"{redteam_pkg.__name__}."
        ):
            if ispkg or modname.endswith(".base"):
                continue
            # Skip template/example modules meant for users, not production
            short_name = modname.split(".")[-1] if "." in modname else modname
            if short_name in ("plugin_template", "plugin_example", "template"):
                continue

            module = _import_module(modname)
            if module is None:
                continue

            self._register_plugin_classes(module)

    def _load_external_plugins(self) -> None:
        """Scan external plugin directories for AttackPlugin subclasses.

        Each directory is treated as a package. Python files found
        directly inside (not in sub-packages) are loaded as modules.
        """
        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.is_dir():
                logger.warning("Plugin directory not found: %s", plugin_dir)
                continue

            # Collect *.py files (skip __init__.py)
            py_files = sorted(plugin_dir.glob("*.py"))
            py_files = [f for f in py_files if f.name != "__init__.py"]

            if not py_files:
                logger.info("No plugin files found in %s", plugin_dir)
                continue

            # Temporarily add to sys.path so we can import them
            sys.path.insert(0, str(plugin_dir.parent))
            try:
                for py_file in py_files:
                    modname = py_file.stem
                    spec = importlib.util.spec_from_file_location(modname, py_file)
                    if spec is None or spec.loader is None:
                        continue
                    try:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self._register_plugin_classes(module)
                    except Exception as e:
                        logger.error(
                            "Failed to load external plugin %s: %s", py_file.name, e
                        )
            finally:
                sys.path.pop(0)

    def _register_plugin_classes(self, module: object) -> None:
        """Find and register all AttackPlugin subclasses in a module."""
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, AttackPlugin)
                and obj is not AttackPlugin
                and not inspect.isabstract(obj)
            ):
                try:
                    plugin = obj()
                    existing = self._plugins.get(plugin.category)
                    self._plugins[plugin.category] = plugin
                    self._scenarios.extend(plugin.get_scenarios())
                    if existing:
                        logger.info(
                            "Plugin '%s' overrode existing plugin for category %s",
                            obj.__name__,
                            plugin.category.value,
                        )
                    else:
                        logger.debug(
                            "Registered plugin '%s' for category %s",
                            obj.__name__,
                            plugin.category.value,
                        )
                except Exception as e:
                    logger.error(
                        "Failed to instantiate plugin %s: %s", obj.__name__, e
                    )


def _import_module(modname: str) -> object | None:
    """Safely import a module by name, returning None on failure."""
    try:
        return importlib.import_module(modname)
    except ImportError as e:
        logger.debug("Skipping %s: %s", modname, e)
        return None
