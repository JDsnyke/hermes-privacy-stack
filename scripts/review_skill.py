#!/usr/bin/env python3
"""Privacy-first wrapper around Hermes' native Skills Hub security pipeline.

The wrapper intentionally does NOT implement its own scanner. Modern Hermes already
quarantines hub bundles and scans them for exfiltration, prompt injection, destructive
commands and supply-chain threats at install time. This wrapper adds project policy:

1. inspect first,
2. explicit acknowledgement for community installs,
3. never expose/forward --force,
4. run the native audit after install,
5. write a local non-secret review receipt outside Git.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

IS_WINDOWS = os.name == "nt"


def state_home() -> Path:
    if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
        return Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
    return Path.home() / ".hermes-privacy-stack-state"


def base(profile: str | None) -> list[str]:
    cmd = ["hermes"]
    if profile:
        cmd += ["-p", profile]
    return cmd


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, text=True, check=check)


def confirm(identifier: str) -> bool:
    print("\nCommunity skills are executable agent instructions and may include helper scripts.")
    print("Installing expands what the selected Hermes profile may choose to do.")
    raw = input(f"Type the skill identifier to approve installation:\n  {identifier}\n> ").strip()
    return raw == identifier


def save_receipt(identifier: str, profile: str | None, install_rc: int, audit_rc: int) -> Path:
    root = state_home() / "skill-reviews"
    root.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in identifier)[:120]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = root / f"{stamp}-{safe}.json"
    payload = {
        "schema": 1,
        "identifier": identifier,
        "profile": profile or "default",
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "workflow": "inspect -> native install security scan -> native audit",
        "force_used": False,
        "install_returncode": install_rc,
        "audit_returncode": audit_rc,
    }
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not IS_WINDOWS:
        try:
            os.chmod(root, 0o700)
            os.chmod(dest, 0o600)
        except OSError:
            pass
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect/audit/install a Hermes skill under privacy-first policy")
    parser.add_argument("identifier", nargs="?", help="Hermes Skills Hub identifier")
    parser.add_argument("--profile", help="Hermes profile to scope the skill operation")
    parser.add_argument("--install", action="store_true", help="Install after inspection and explicit approval")
    parser.add_argument("--yes", action="store_true", help="Approve install non-interactively (CI/automation only)")
    parser.add_argument("--audit", action="store_true", help="Audit currently installed skills only")
    parser.add_argument("--browse-official", action="store_true", help="Browse official optional skills")
    args = parser.parse_args()

    if not shutil.which("hermes"):
        raise SystemExit("Hermes CLI is required.")

    prefix = base(args.profile)

    if args.audit:
        return run(prefix + ["skills", "audit"], check=False).returncode
    if args.browse_official:
        return run(prefix + ["skills", "browse", "--source", "official"], check=False).returncode
    if not args.identifier:
        parser.error("identifier is required unless --audit or --browse-official is used")

    identifier = args.identifier.strip()
    if identifier.startswith("-") or not identifier:
        raise SystemExit("Invalid skill identifier.")

    print("\n=== Inspection (no install) ===")
    inspected = run(prefix + ["skills", "inspect", identifier], check=False)
    if inspected.returncode:
        print("Inspection failed; refusing installation.")
        return inspected.returncode

    if not args.install:
        print("\nInspection complete. Re-run with --install after reviewing the source, license and requested authority.")
        return 0

    if not args.yes and not confirm(identifier):
        print("Approval did not match identifier; nothing installed.")
        return 2

    print("\n=== Native Hermes install/security scan ===")
    # Never pass --force. Hermes' normal security policy remains authoritative.
    installed = run(prefix + ["skills", "install", identifier, "--yes"], check=False)
    if installed.returncode:
        receipt = save_receipt(identifier, args.profile, installed.returncode, -1)
        print(f"Install failed/blocked. Receipt: {receipt}")
        return installed.returncode

    print("\n=== Post-install native audit ===")
    audited = run(prefix + ["skills", "audit"], check=False)
    receipt = save_receipt(identifier, args.profile, installed.returncode, audited.returncode)
    print(f"Local review receipt: {receipt}")
    if audited.returncode:
        print("Audit reported a problem. Treat the skill as untrusted until reviewed/disabled or removed.")
        return audited.returncode

    print("✓ Skill installed through Hermes' native security pipeline; no --force override was used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
