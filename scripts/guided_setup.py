#!/usr/bin/env python3
"""Interactive post-bootstrap setup for profiles, SOUL, integrations and persistence approvals.

Runs only after the core bootstrap succeeds. It never asks for credentials or personal
facts. Answers are behavioral/security choices and local profile selections.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = os.name == "nt"


def state_home() -> Path:
    if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
        return Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
    return Path.home() / ".hermes-privacy-stack-state"


def yesno(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n] " if default else " [y/N] "
    raw = input(prompt + suffix).strip().lower()
    return default if not raw else raw in {"y", "yes"}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True)


def load_install_state() -> dict:
    path = state_home() / "install.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def set_config(key: str, value: str) -> None:
    run(["hermes", "config", "set", key, value], check=False)


def configure_write_gates() -> None:
    set_config("memory.write_approval", "true")
    set_config("skills.write_approval", "true")
    set_config("skills.guard_agent_created", "true")
    print("✓ Enabled approval gates for Hermes memory/skill writes and agent-created skill scanning.")
    print("  Review staged writes with /memory pending and /skills pending in supported surfaces.")


def install_profiles(preset: str, role: str) -> None:
    if role == "server":
        default_profiles = False
    else:
        default_profiles = preset in {"balanced", "developer"}
    if not yesno("Create isolated starter profiles (private-personal, coder, researcher)?", default_profiles):
        return

    lean_default = preset == "strict"
    lean = yesno("Create those profiles in lean mode (no full bundled-skill seed)?", lean_default)
    cmd = [sys.executable, str(ROOT / "scripts" / "install_profiles.py"), "private-personal", "coder", "researcher"]
    if lean:
        cmd.append("--lean")
    run(cmd, check=False)

    if yesno("Also create the high-authority operator profile?", False):
        cmd = [sys.executable, str(ROOT / "scripts" / "install_profiles.py"), "operator"]
        if lean:
            cmd.append("--lean")
        run(cmd, check=False)


def customize_default_soul() -> None:
    if not yesno("Customize the default Hermes personality/SOUL now?", False):
        return
    print("The builder asks only behavioral preferences and previews a diff before writing.")
    run([sys.executable, str(ROOT / "scripts" / "build_personality.py"), "--profile", "default", "--apply"], check=False)


def setup_nango(preset: str, role: str) -> None:
    if role == "client":
        return
    if not yesno("Enable optional Nango Free Self-Hosted for OAuth/API credential management and proxying?", False):
        return
    print("Nango Free Self-Hosted is used here for Auth + Proxy only.")
    print("Functions, webhooks, managed MCP and the full runtime are not assumed in the free self-host profile.")
    run([sys.executable, str(ROOT / "scripts" / "setup_nango.py")], check=False)


def mark_complete(state: dict) -> None:
    root = state_home()
    root.mkdir(parents=True, exist_ok=True)
    path = root / "guided.json"
    payload = {
        "schema": 2,
        "completed": True,
        "preset": state.get("preset"),
        "role": state.get("role"),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not IS_WINDOWS:
        try:
            os.chmod(root, 0o700)
            os.chmod(path, 0o600)
        except OSError:
            pass


def already_complete() -> bool:
    path = state_home() / "guided.json"
    if not path.exists():
        return False
    try:
        return bool(json.loads(path.read_text(encoding="utf-8")).get("completed"))
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive privacy/profile hardening after core bootstrap")
    parser.add_argument("--force", action="store_true", help="Run again even if guided setup was previously completed")
    args = parser.parse_args()

    if not shutil.which("hermes"):
        print("Hermes CLI not found; skipping guided profile/privacy setup.")
        return 0

    if already_complete() and not args.force:
        print("Guided setup was already completed. Run `python scripts/guided_setup.py --force` to revisit it.")
        return 0

    state = load_install_state()
    preset = str(state.get("preset") or "balanced")
    role = str(state.get("role") or "local")

    print("\nHermes Privacy Stack — guided profile, integration & persistence setup")
    print("No credentials or personal profile facts are requested here.\n")

    install_profiles(preset, role)
    customize_default_soul()
    setup_nango(preset, role)

    gate_default = preset in {"strict", "balanced"}
    if yesno("Require approval before Hermes persists agent-created memory/skill writes?", gate_default):
        configure_write_gates()
    else:
        print("ℹ Persistence approval gates left unchanged.")

    if yesno("Run Hermes configuration validation now?", True):
        run(["hermes", "config", "check"], check=False)

    mark_complete(state)
    print("\n✓ Guided setup complete.")
    print("Review skills with: python scripts/review_skill.py --browse-official")
    print("Revisit these choices with: python scripts/guided_setup.py --force")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
