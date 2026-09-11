#!/usr/bin/env python3
"""Restore Hermes Privacy Stack v2 backup artifacts safely.

Shared mcp-memory-service database restore is intentionally not automated yet. The
script refuses to restore live service databases until a consistency-safe procedure
is implemented and tested.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

IS_WINDOWS = os.name == "nt"


def hermes_home() -> Path:
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    return Path.home() / ".hermes"


def run(cmd: list[str], check: bool = True):
    print("+", " ".join(map(str, cmd)))
    return subprocess.run(cmd, check=check)


def safe_members(tf: tarfile.TarFile, destination: Path):
    base = destination.resolve()
    for member in tf.getmembers():
        target = (destination / member.name).resolve()
        try:
            target.relative_to(base)
        except ValueError as exc:
            raise SystemExit(f"Unsafe path in archive: {member.name}") from exc
        if member.issym() or member.islnk():
            raise SystemExit(f"Links are not allowed in safe config archives: {member.name}")
        yield member


def restore_safe_config(archive: Path, force: bool) -> None:
    target = hermes_home()
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tf:
        members = list(safe_members(tf, target))
        conflicts = [m.name for m in members if (target / m.name).exists()]
        if conflicts and not force:
            preview = "\n  ".join(conflicts[:12])
            raise SystemExit("Refusing to overwrite existing Hermes config. Re-run with --force after reviewing:\n  " + preview)
        tf.extractall(target, members=members)
    print(f"Restored sanitized config archive into {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore Hermes Privacy Stack v2 backup artifacts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--safe-config", type=Path, help="Restore sanitized config tar.gz made by backup.py")
    group.add_argument("--hermes-full", type=Path, help="Restore full native Hermes backup ZIP")
    group.add_argument(
        "--memory-database",
        type=Path,
        help="Reserved safety gate; currently refuses live/shared SQLite restore until the tested procedure lands",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.safe_config:
        restore_safe_config(args.safe_config.expanduser().resolve(), args.force)
    elif args.hermes_full:
        if not shutil.which("hermes"):
            raise SystemExit("Hermes is required for native full restore.")
        print("! Full backups may contain OAuth/API credentials. Restore only from a trusted encrypted source.")
        cmd = ["hermes", "import", str(args.hermes_full.expanduser().resolve())]
        if args.force:
            cmd.append("--force")
        run(cmd)
    else:
        raise SystemExit(
            "Automated mcp-memory-service database restore is not release-ready. "
            "Refusing to replace a live SQLite database. Follow docs/BACKUP-RESTORE.md."
        )

    print("Restore completed. Run `python scripts/doctor.py` and representative functional checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
