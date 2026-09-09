#!/usr/bin/env python3
"""Pure integration check for bootstrap-generated Hindsight profile-bank config.

Runs against a temporary HERMES_HOME and never requires Hermes, Docker, OAuth, or a
live Hindsight server. The test exists to catch drift in the multi-profile memory
contract independently from the heavier retain/recall/reflect workflow.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_PATH = ROOT / "bootstrap.py"


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("hps_bootstrap_test", BOOTSTRAP_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load {BOOTSTRAP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise SystemExit(f"Malformed env line: {raw!r}")
        values[key] = value
    return values


def main() -> int:
    old_home = os.environ.get("HERMES_HOME")
    old_state = os.environ.get("HERMES_PRIVACY_STACK_STATE")
    try:
        with tempfile.TemporaryDirectory(prefix="hps-hindsight-config-") as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes"
            state_home = root / "state"
            os.environ["HERMES_HOME"] = str(hermes_home)
            os.environ["HERMES_PRIVACY_STACK_STATE"] = str(state_home)

            bootstrap = load_bootstrap()
            api_url = "http://127.0.0.1:18888/"
            bootstrap.configure_hindsight(api_url)

            config_path = hermes_home / "hindsight" / "config.json"
            env_path = hermes_home / ".env"
            if not config_path.exists() or not env_path.exists():
                raise SystemExit("configure_hindsight did not create expected local files")

            config = json.loads(config_path.read_text(encoding="utf-8"))
            expected = {
                "mode": "local_external",
                "api_url": "http://127.0.0.1:18888",
                "bank_id": "hermes",
                "bank_id_template": "hermes-{profile}",
                "auto_retain": True,
                "auto_recall": True,
            }
            for key, value in expected.items():
                actual = config.get(key)
                if actual != value:
                    raise SystemExit(f"Hindsight config mismatch for {key}: {actual!r} != {value!r}")

            env = parse_env(env_path)
            if env.get("HINDSIGHT_API_URL") != "http://127.0.0.1:18888":
                raise SystemExit("HINDSIGHT_API_URL was not written/normalized correctly")

            # The temporary test must not create auth, USER.md, MEMORY.md, sessions,
            # or other user-owned state as a side effect.
            forbidden = [
                hermes_home / "USER.md",
                hermes_home / "MEMORY.md",
                hermes_home / "auth.json",
                hermes_home / "sessions",
            ]
            leaked = [str(path) for path in forbidden if path.exists()]
            if leaked:
                raise SystemExit("Unexpected user-state side effects: " + ", ".join(leaked))

            print("Hindsight profile-bank config test passed")
            print("bank_id_template=hermes-{profile}")
            print("api_url=http://127.0.0.1:18888")
            return 0
    finally:
        if old_home is None:
            os.environ.pop("HERMES_HOME", None)
        else:
            os.environ["HERMES_HOME"] = old_home
        if old_state is None:
            os.environ.pop("HERMES_PRIVACY_STACK_STATE", None)
        else:
            os.environ["HERMES_PRIVACY_STACK_STATE"] = old_state


if __name__ == "__main__":
    raise SystemExit(main())
