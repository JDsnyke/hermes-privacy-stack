#!/usr/bin/env python3
"""Create privacy-aware backups for Hermes Privacy Stack.

Modes:
- safe (default): config/skills/personality only; excludes credentials, USER.md,
  MEMORY.md, sessions and databases.
- full: delegates to `hermes backup`, which intentionally includes credentials
  and must be encrypted before cloud storage.

Hindsight banks are exported logically with `hindsight-admin export-bank` from
inside the running container. Live database files are never copied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import time
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return cleaned or "bank"


def create_safe_config_archive(destination: Path) -> Path:
    h = hermes_home()
    allow = ["config.yaml", "SOUL.md", "AGENTS.md", "skills", "cron", "scripts", "hindsight/config.json"]
    with tarfile.open(destination, "w:gz") as tf:
        for rel in allow:
            source = h / rel
            if source.exists():
                tf.add(source, arcname=rel, recursive=True)
    return destination


def compose_base() -> list[str]:
    env = state_home() / "stack.env"
    return ["docker", "compose", "--env-file", str(env), "-f", str(ROOT / "stack" / "compose.yml"), "--profile", "core"]


def export_bank(bank: str, destination: Path, include_history: bool) -> Path:
    if not shutil.which("docker"):
        raise SystemExit("Docker is required for Hindsight logical bank export.")
    if not (state_home() / "stack.env").exists():
        raise SystemExit("Generated stack.env not found; this helper expects a locally managed Hindsight container.")

    container_path = f"/tmp/hps-{safe_name(bank)}-{int(time.time())}.zip"
    cmd = compose_base() + ["exec", "-T", "hindsight", "hindsight-admin", "export-bank", "--bank", bank, "--output", container_path]
    if include_history:
        cmd.append("--include-history")
    run(cmd)
    run(compose_base() + ["cp", f"hindsight:{container_path}", str(destination)])
    run(compose_base() + ["exec", "-T", "hindsight", "rm", "-f", container_path], check=False)
    return destination


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", help="Backup parent directory.")
    p.add_argument("--mode", choices=["safe", "full"], default="safe")
    p.add_argument("--bank", action="append", default=[], help="Hindsight bank to export; repeatable.")
    p.add_argument("--include-history", action="store_true", help="Include Hindsight audit/LLM history in bank exports.")
    p.add_argument("--rclone-dest", help="Optional preconfigured *encrypted* rclone crypt destination, e.g. drivecrypt:hermes.")
    p.add_argument("--confirm-rclone-crypt", action="store_true", help="Required with --rclone-dest; confirms the destination is an rclone crypt remote.")
    args = p.parse_args()

    state = state_home()
    parent = Path(args.output).expanduser() if args.output else state / "backups"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bundle = parent / f"hps-{stamp}"
    bundle.mkdir(parents=True, exist_ok=False)
    artifacts: list[Path] = []

    if args.mode == "safe":
        config_archive = bundle / "hermes-config-safe.tar.gz"
        create_safe_config_archive(config_archive)
        artifacts.append(config_archive)
        print(f"Created sanitized config archive: {config_archive}")
    else:
        if not shutil.which("hermes"):
            raise SystemExit("Hermes is required for --mode full.")
        full = bundle / "hermes-full.zip"
        print("! Full Hermes backups include .env/auth credentials. Encrypt before cloud storage.")
        run(["hermes", "backup", "-o", str(full)])
        artifacts.append(full)

    for bank in args.bank:
        target = bundle / f"hindsight-{safe_name(bank)}.zip"
        export_bank(bank, target, args.include_history)
        artifacts.append(target)
        print(f"Exported Hindsight bank {bank!r}: {target}")

    manifest = {
        "schema": 1,
        "created_at": stamp,
        "mode": args.mode,
        "contains_credentials": args.mode == "full",
        "hindsight_banks": args.bank,
        "files": [{"name": item.name, "size": item.stat().st_size, "sha256": sha256(item)} for item in artifacts],
    }
    manifest_path = bundle / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.rclone_dest:
        if not args.confirm_rclone_crypt:
            raise SystemExit("--rclone-dest requires --confirm-rclone-crypt. The tool cannot safely infer your remote's encryption policy.")
        if not shutil.which("rclone"):
            raise SystemExit("rclone is not installed.")
        run(["rclone", "copy", str(bundle), args.rclone_dest, "--create-empty-src-dirs"])
        print(f"Copied bundle to confirmed encrypted rclone destination: {args.rclone_dest}")

    print(f"\nBackup complete: {bundle}")
    print("Keep at least one restore-tested copy on storage independent of the machine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
