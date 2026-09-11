#!/usr/bin/env python3
"""Run strict-free v2 bootstrap twice in an isolated temporary home.

External commands are stubbed; the test verifies installer-owned state changes never
overwrite user-owned Hermes files or rotate generated service secrets.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_PATH = ROOT / "bootstrap.py"


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("hps_bootstrap_idempotency", BOOTSTRAP_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load {BOOTSTRAP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    old_home = os.environ.get("HERMES_HOME")
    old_state = os.environ.get("HERMES_PRIVACY_STACK_STATE")
    old_argv = sys.argv[:]
    try:
        with tempfile.TemporaryDirectory(prefix="hps-v2-idempotency-") as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes"
            state_home = root / "state"
            os.environ["HERMES_HOME"] = str(hermes_home)
            os.environ["HERMES_PRIVACY_STACK_STATE"] = str(state_home)
            bootstrap = load_bootstrap()
            calls: list[list[str] | str] = []

            def fake_command(name: str):
                return "hermes-test-stub" if name == "hermes" else None

            def fake_run(cmd, check=True, shell=False, capture=False):
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            bootstrap.command = fake_command
            bootstrap.run = fake_run
            bootstrap.detect_runtime = lambda: None
            args = [
                str(BOOTSTRAP_PATH), "--preset", "balanced", "--role", "local",
                "--model-provider", "skip", "--non-interactive",
            ]

            sys.argv = args
            if bootstrap.main() != 0:
                raise SystemExit("first bootstrap run failed")

            soul = hermes_home / "SOUL.md"
            user = hermes_home / "USER.md"
            env_file = hermes_home / ".env"
            auth = hermes_home / "auth.json"
            config = hermes_home / "config.yaml"
            stack_env = state_home / "stack.env"
            searx = state_home / "runtime" / "searxng" / "settings.yml"
            for path in (soul, user, env_file, stack_env, searx, state_home / "install.json"):
                if not path.exists():
                    raise SystemExit(f"first run missed expected file: {path}")

            first_stack_env = stack_env.read_text(encoding="utf-8")
            first_searx = searx.read_text(encoding="utf-8")
            if "__HPS_SEARXNG_SECRET__" in first_searx:
                raise SystemExit("runtime SearXNG marker was not replaced")
            if "HPS_MEMORY_API_KEY=" not in first_stack_env or "HPS_NODERED_CREDENTIAL_SECRET=" not in first_stack_env:
                raise SystemExit("generated strict-free service secrets missing")

            custom_soul = "# User-owned SOUL\n\nHPS-IDEMPOTENT-SOUL\n"
            custom_user = "# User\n\nHPS-IDEMPOTENT-USER\n"
            soul.write_text(custom_soul, encoding="utf-8")
            user.write_text(custom_user, encoding="utf-8")
            with env_file.open("a", encoding="utf-8") as handle:
                handle.write("HPS_FAKE_PRIVATE_TOKEN=do-not-overwrite\n")
            auth.write_text('{"fake":"credential-state"}\n', encoding="utf-8")
            config.write_text("user_owned_setting: keep-me\n", encoding="utf-8")
            before_auth = auth.read_text(encoding="utf-8")
            before_config = config.read_text(encoding="utf-8")

            sys.argv = args
            if bootstrap.main() != 0:
                raise SystemExit("second bootstrap run failed")

            assertions = {
                "SOUL.md": soul.read_text(encoding="utf-8") == custom_soul,
                "USER.md": user.read_text(encoding="utf-8") == custom_user,
                "auth.json": auth.read_text(encoding="utf-8") == before_auth,
                "config.yaml": config.read_text(encoding="utf-8") == before_config,
                "SearXNG secret": searx.read_text(encoding="utf-8") == first_searx,
                "stack secrets": stack_env.read_text(encoding="utf-8") == first_stack_env,
                "private env material": "HPS_FAKE_PRIVATE_TOKEN=do-not-overwrite" in env_file.read_text(encoding="utf-8"),
            }
            failed = [name for name, ok in assertions.items() if not ok]
            if failed:
                raise SystemExit("idempotency failure: " + ", ".join(failed))

            final_env = env_file.read_text(encoding="utf-8").splitlines()
            for key in ("MCP_MEMORY_API_KEY", "SEARXNG_URL"):
                count = sum(1 for line in final_env if line.startswith(key + "="))
                if count != 1:
                    raise SystemExit(f"expected one {key}, found {count}")

            state = json.loads((state_home / "install.json").read_text(encoding="utf-8"))
            if state.get("architecture") != "strict-free-v2" or state.get("bind_address") != "127.0.0.1":
                raise SystemExit("install state drifted")
            if not any(isinstance(call, list) and call[:3] == ["hermes", "config", "check"] for call in calls):
                raise SystemExit("Hermes config validation was not exercised")

            print("bootstrap strict-free v2 twice-run idempotency test passed")
            return 0
    finally:
        sys.argv = old_argv
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
