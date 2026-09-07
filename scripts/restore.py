#!/usr/bin/env python3
"""Restore Hermes Privacy Stack backups without copying live database files."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def compose_base() -> list[str]:
    env = state_home() / "stack.env"
    return ["docker", "compose", "--env-file", str(env), "-f", str(ROOT / "stack" / "compose.yml"), "--profile", "core"]


def import_bank(archive: Path, target_bank: str | None) -> None:
    if not shutil.which("docker"):
        raise SystemExit("Docker is required to import a bank into the managed Hindsight container.")
    if not (state_home() / "stack.env").exists():
        raise SystemExit("Generated stack.env not found.")

    with tempfile.NamedTemporaryFile(prefix="hps-import-", suffix=".zip", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        shutil.copy2(archive, tmp_path)
        container_path = f"/tmp/{tmp_path.name}"
        run(compose_base() + ["cp", str(tmp_path), f"hindsight:{container_path}"])
        cmd = compose_base() + ["exec", "-T", "hindsight", "hindsight-admin", "import-bank", "--archive", container_path]
        if target_bank:
            cmd += ["--target-bank", target_bank]
        run(cmd)
        run(compose_base() + ["exec", "-T", "hindsight", "rm", "-f", container_path], check=False)
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> int:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--safe-config", type=Path, help="Restore a sanitized config tar.gz made by backup.py.")
    group.add_argument("--hermes-full", type=Path, help="Restore a full native Hermes backup ZIP (contains credentials).")
    group.add_argument("--hindsight-bank", type=Path, help="Import a Hindsight export-bank ZIP.")
    p.add_argument("--target-bank", help="Override Hindsight bank id during import.")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

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
        import_bank(args.hindsight_bank.expanduser().resolve(), args.target_bank)

    print("Restore operation completed. Run `python scripts/doctor.py` and perform representative recall tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
