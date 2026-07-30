#!/usr/bin/env python3
"""Read/write certifyai.yaml from the project root.

Usage:
  python3 config_io.py read          → prints JSON config to stdout
  echo '{"provider":...}' | python3 config_io.py write   → reads JSON from stdin, writes YAML
"""

import json
import sys
from pathlib import Path

import yaml

LIB_DIR = Path(__file__).resolve().parent  # certifyai/web/lib/
PROJECT_ROOT = LIB_DIR.parent.parent.parent  # lib/ → web/ → certifyai/ → project root
CONFIG_PATH = PROJECT_ROOT / "certifyai.yaml"

DEFAULT_CONFIG = {
    "provider": {"name": "openai", "model": "gpt-4o", "api_key": ""},
    "paths": {"vault": "./certifyai_vault", "database": "certifyai.db", "concurrency": "3"},
    "frameworks": ["eu_ai_act", "soc2", "nist_ai_rmf"],
    "reports": {"output": "./reports/compliance.json"},
}


def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as f:
            cfg = yaml.safe_load(f) or {}
            return deep_merge(dict(DEFAULT_CONFIG), cfg)
    return dict(DEFAULT_CONFIG)


def save(cfg: dict) -> None:
    with CONFIG_PATH.open("w") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: config_io.py read|write"}))
        sys.exit(1)

    action = sys.argv[1]
    try:
        if action == "read":
            print(json.dumps(load()))
        elif action == "write":
            raw = sys.stdin.read()
            data = json.loads(raw)
            save(data)
            print(json.dumps({"status": "ok", "path": str(CONFIG_PATH)}))
        else:
            print(json.dumps({"error": f"Unknown action: {action}"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
