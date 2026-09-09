#!/usr/bin/env python3
"""Run the non-interactive bootstrap twice in an isolated temporary home.

The test stubs external Hermes CLI calls and deliberately makes Docker unavailable, so
it validates installer state ownership without network access. Between runs it edits
user-owned files and adds fake credential material; the second run must preserve all
of it as well as the generated SearXNG secret.
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
        with tempfile.TemporaryDirectory(prefix="hps-idempotency-") as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes"
            state_home = root / "state"
            os.environ["HERMES_HOME"] = str(hermes_home)
            os.environ["HERMES_PRIVACY_STACK_STATE"] = str(state_home)

            bootstrap = load_bootstrap()
            calls: list[list[str] | str] = []

            def fake_command(name: str):
                # Pretend Hermes exists so the official installer/model flow is never
                # invoked. Pretend Docker does not exist so no external services start.
                return "hermes-test-stub" if name == "hermes" else None

            def fake_run(cmd, check=True, shell=False, capture=False):
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            bootstrap.command = fake_command
            bootstrap.run = fake_run

            args = [
                str(BOOTSTRAP_PATH),
                "--preset",
                "balanced",
                "--role",
                "local",
                "--non-interactive",
                "--skip-model-setup",
            ]

            # First bootstrap creates only installer-owned defaults/runtime state.
            sys.argv = args
            if bootstrap.main() != 0:
                raise SystemExit("first bootstrap run failed")

            soul = hermes_home / "SOUL.md"
            user = hermes_home / "USER.md"
            env_file = hermes_home / ".env"
            auth = hermes_home / "auth.json"
            config = hermes_home / "config.yaml"
            searx_settings = state_home / "runtime" / "searxng" / "settings.yml"

            required = [soul, user, env_file, searx_settings, state_home / "install.json"]
            missing = [str(path) for path in required if not path.exists()]
            if missing:
                raise SystemExit("first run missed expected files: " + ", ".join(missing))

            first_secret_config = searx_settings.read_text(encoding="utf-8")
            if "__HPS_SEARXNG_SECRET__" in first_secret_config:
                raise SystemExit("runtime SearXNG secret marker was not replaced")

            # Simulate user ownership/customization after install.
            custom_soul = "# User-owned SOUL\n\nNever overwrite this marker: HPS-IDEMPOTENT-SOUL\n"
            custom_user = "# User\n\nUser-owned durable context marker: HPS-IDEMPOTENT-USER\n"
            soul.write_text(custom_soul, encoding="utf-8")
            user.write_text(custom_user, encoding="utf-8")
            with env_file.open("a", encoding="utf-8") as handle:
                handle.write("HPS_FAKE_PRIVATE_TOKEN=do-not-overwrite\n")
            auth.write_text('{"fake":"credential-state"}\n', encoding="utf-8")
            config.write_text("user_owned_setting: keep-me\n", encoding="utf-8")

            before_env = env_file.read_text(encoding="utf-8")
            before_auth = auth.read_text(encoding="utf-8")
            before_config = config.read_text(encoding="utf-8")

            # Second run must update its own generated state while preserving user data.
            sys.argv = args
            if bootstrap.main() != 0:
                raise SystemExit("second bootstrap run failed")

            assertions = {
                "SOUL.md": soul.read_text(encoding="utf-8") == custom_soul,
                "USER.md": user.read_text(encoding="utf-8") == custom_user,
                "auth.json": auth.read_text(encoding="utf-8") == before_auth,
                "config.yaml": config.read_text(encoding="utf-8") == before_config,
                "SearXNG runtime secret": searx_settings.read_text(encoding="utf-8") == first_secret_config,
                "fake credential env line": "HPS_FAKE_PRIVATE_TOKEN=do-not-overwrite" in env_file.read_text(encoding="utf-8"),
            }
            failed = [name for name, ok in assertions.items() if not ok]
            if failed:
                raise SystemExit("idempotency failure: " + ", ".join(failed))

            # Installer-managed env keys must be updated in place, not duplicated.
            final_env_lines = env_file.read_text(encoding="utf-8").splitlines()
            for key in ("HINDSIGHT_API_URL", "SEARXNG_URL"):
                count = sum(1 for line in final_env_lines if line.startswith(key + "="))
                if count != 1:
                    raise SystemExit(f"expected exactly one {key} entry after rerun, found {count}")

            install_state = json.loads((state_home / "install.json").read_text(encoding="utf-8"))
            if install_state.get("role") != "local" or install_state.get("bind_address") != "127.0.0.1":
                raise SystemExit("generated install state drifted during idempotency test")

            if before_env == env_file.read_text(encoding="utf-8"):
                # This is not a requirement, just protect the test from accidentally
                # becoming vacuous if bootstrap stops managing its expected env keys.
                if "HINDSIGHT_API_URL=" not in before_env or "SEARXNG_URL=" not in before_env:
                    raise SystemExit("test fixture did not contain bootstrap-managed env keys")

            if not any(isinstance(call, list) and call[:3] == ["hermes", "config", "check"] for call in calls):
                raise SystemExit("stubbed Hermes config validation was never exercised")

            print("bootstrap twice-run idempotency test passed")
            print("preserved: SOUL.md, USER.md, auth.json, config.yaml, private env material, SearXNG secret")
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
