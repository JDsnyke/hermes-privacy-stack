#!/usr/bin/env python3
"""Create privacy-aware Hermes Privacy Stack v2 backup bundles.

This script intentionally does NOT copy live service databases. Until the dedicated
mcp-memory-service consistency-safe backup helper lands, shared memory must be backed
up using the upstream/service-safe procedure described in docs/BACKUP-RESTORE.md.

Modes:
- safe: sanitized Hermes config/personality/skills only.
- full: delegates to Hermes native backup and therefore may contain credentials.

Optional restic support snapshots the completed bundle. Repository/password/backend
credentials are read by restic from its normal environment/config; this script never
accepts a backup password on the command line.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

IS_WINDOWS = os.name == "nt"


def hermes_home() -> Path:
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    return Path.home() / ".hermes"


def state_home() -> Path:
    if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
        return Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
    return Path.home() / ".hermes-privacy-stack-state"


def run(cmd: list[str], check: bool = True):
    print("+", " ".join(map(str, cmd)))
    return subprocess.run(cmd, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_safe_config_archive(destination: Path) -> Path:
    home = hermes_home()
    allow = ["config.yaml", "SOUL.md", "AGENTS.md", "skills", "cron", "scripts"]
    with tarfile.open(destination, "w:gz") as tf:
        for rel in allow:
            source = home / rel
            if source.exists():
                tf.add(source, arcname=rel, recursive=True)
    return destination


def restic_backup(bundle: Path) -> None:
    if not shutil.which("restic"):
        raise SystemExit("restic is not installed.")
    if not os.environ.get("RESTIC_REPOSITORY"):
        raise SystemExit("Set RESTIC_REPOSITORY in the environment before using --restic.")
    if not (os.environ.get("RESTIC_PASSWORD") or os.environ.get("RESTIC_PASSWORD_FILE") or os.environ.get("RESTIC_PASSWORD_COMMAND")):
        raise SystemExit(
            "Configure restic authentication with RESTIC_PASSWORD, RESTIC_PASSWORD_FILE, "
            "or RESTIC_PASSWORD_COMMAND. Passwords are never accepted as CLI arguments here."
        )
    run(["restic", "backup", str(bundle), "--tag", "hermes-privacy-stack", "--tag", "strict-free-v2"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Hermes Privacy Stack v2 backups")
    parser.add_argument("--output", help="Backup parent directory")
    parser.add_argument("--mode", choices=["safe", "full"], default="safe")
    parser.add_argument("--restic", action="store_true", help="Snapshot the completed bundle using configured restic environment")
    parser.add_argument(
        "--include-memory",
        action="store_true",
        help="Reserved safety gate; currently refuses because live SQLite copying is not a supported backup method.",
    )
    args = parser.parse_args()

    if args.include_memory:
        raise SystemExit(
            "Automated mcp-memory-service backup is not release-ready yet. Refusing to copy the live SQLite volume. "
            "Follow docs/BACKUP-RESTORE.md for the current service-safe procedure."
        )

    parent = Path(args.output).expanduser() if args.output else state_home() / "backups"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bundle = parent / f"hps-v2-{stamp}"
    bundle.mkdir(parents=True, exist_ok=False)
    artifacts: list[Path] = []

    if args.mode == "safe":
        archive = create_safe_config_archive(bundle / "hermes-config-safe.tar.gz")
        artifacts.append(archive)
        contains_credentials = False
    else:
        if not shutil.which("hermes"):
            raise SystemExit("Hermes is required for --mode full.")
        archive = bundle / "hermes-full.zip"
        print("! Full Hermes backups may contain OAuth/API credentials. Keep the backup encrypted.")
        run(["hermes", "backup", "-o", str(archive)])
        artifacts.append(archive)
        contains_credentials = True

    manifest = {
        "schema": 2,
        "architecture": "strict-free-v2",
        "created_at": stamp,
        "mode": args.mode,
        "contains_credentials": contains_credentials,
        "shared_memory_included": False,
        "note": "mcp-memory-service database intentionally excluded until consistency-safe automated backup is implemented",
        "files": [{"name": item.name, "size": item.stat().st_size, "sha256": sha256(item)} for item in artifacts],
    }
    manifest_path = bundle / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.restic:
        restic_backup(bundle)
        print("restic snapshot completed")

    print(f"\nBackup bundle: {bundle}")
    print("Shared semantic-memory data is NOT included by this command yet.")
    print("Run restore drills before relying on any backup as your only copy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
