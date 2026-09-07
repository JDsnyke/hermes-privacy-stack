#!/usr/bin/env python3
"""Install reviewed Hermes profile/SOUL starter bundles without copying credentials.

This script deliberately uses `hermes profile create` without --clone/--clone-all.
Profiles therefore start with fresh local state instead of copying `.env`, auth, memory,
or sessions from another profile. Existing SOUL.md files are never overwritten unless
--force-soul is explicitly supplied.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "profiles"
IS_WINDOWS = os.name == "nt"

DESCRIPTIONS = {
    "private-personal": "Privacy-first personal assistant with conservative memory/tool authority.",
    "coder": "Software-engineering profile for reviewable, secure implementation.",
    "researcher": "Evidence-first research profile with source/recency discipline.",
    "operator": "Infrastructure and automation profile with rollback/change discipline.",
}


def hermes_home() -> Path:
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    return Path.home() / ".hermes"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True)


def available() -> list[str]:
    return sorted(p.parent.name for p in TEMPLATES.glob("*/SOUL.md"))


def profile_dir(name: str) -> Path:
    return hermes_home() / "profiles" / name


def install_one(name: str, force_soul: bool, alias: bool, dry_run: bool) -> None:
    source = TEMPLATES / name / "SOUL.md"
    if not source.exists():
        raise SystemExit(f"Unknown profile bundle: {name}")

    target_dir = profile_dir(name)
    target_soul = target_dir / "SOUL.md"

    if not target_dir.exists():
        cmd = ["hermes", "profile", "create", name, "--no-alias"]
        if dry_run:
            print("DRY RUN:", " ".join(cmd))
        else:
            run(cmd)
    else:
        print(f"ℹ Profile already exists: {name}")

    if target_soul.exists() and not force_soul:
        print(f"↷ Preserving existing {target_soul}; use --force-soul to replace it.")
    else:
        if dry_run:
            print(f"DRY RUN: copy {source} -> {target_soul}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_soul.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"✓ Installed SOUL for {name}")

    description = DESCRIPTIONS.get(name)
    if description:
        cmd = ["hermes", "profile", "describe", name, description]
        if dry_run:
            print("DRY RUN:", " ".join(cmd))
        else:
            run(cmd, check=False)

    if alias:
        cmd = ["hermes", "profile", "alias", name]
        if dry_run:
            print("DRY RUN:", " ".join(cmd))
        else:
            run(cmd, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Hermes Privacy Stack profile bundles")
    parser.add_argument("profiles", nargs="*", help="Bundle names, or 'all'")
    parser.add_argument("--list", action="store_true", help="List bundled profiles")
    parser.add_argument("--force-soul", action="store_true", help="Replace an existing profile SOUL.md")
    parser.add_argument("--alias", action="store_true", help="Create Hermes shell aliases")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bundles = available()
    if args.list:
        for name in bundles:
            print(f"{name}: {DESCRIPTIONS.get(name, '')}")
        return 0

    if not shutil.which("hermes"):
        raise SystemExit("Hermes CLI is required. Install the core stack first.")

    requested = args.profiles or ["private-personal", "coder", "researcher"]
    if "all" in requested:
        requested = bundles

    unknown = sorted(set(requested) - set(bundles))
    if unknown:
        raise SystemExit("Unknown profile bundle(s): " + ", ".join(unknown))

    for name in requested:
        install_one(name, args.force_soul, args.alias, args.dry_run)

    print("\nProfiles installed without cloning credentials or memory.")
    print("Configure model/auth for each profile using Hermes' own setup/model flow as needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
