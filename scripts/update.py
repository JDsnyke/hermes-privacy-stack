#!/usr/bin/env python3
"""Safe updater for Hermes Privacy Stack.

This updates *this repository*. Hermes itself is only upgraded when --hermes is
explicitly requested. The updater refuses a dirty checkout, records the current
commit, takes a native Hermes quick backup, validates the new tree, and can roll
the repository back automatically if static validation fails.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], check: bool = True, capture: bool = False):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def git(*args: str, check: bool = True, capture: bool = False):
    return run(["git", "-C", str(ROOT), *args], check=check, capture=capture)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="Fetch metadata and show whether the stack repo is behind.")
    p.add_argument("--hermes", action="store_true", help="Also run Hermes' own safe updater with a full pre-update backup.")
    p.add_argument("--services", action="store_true", help="Pull/recreate enabled Compose services after repository update.")
    p.add_argument("--no-rollback", action="store_true", help="Do not automatically restore the old repo commit if validation fails.")
    args = p.parse_args()

    if not shutil.which("git"):
        raise SystemExit("git is required")
    status = git("status", "--porcelain", capture=True).stdout.strip()
    if status:
        raise SystemExit("Refusing to update a dirty checkout. Commit/stash your changes first.")

    old = git("rev-parse", "HEAD", capture=True).stdout.strip()
    git("fetch", "--prune")

    if args.check:
        upstream = git("rev-parse", "@{u}", capture=True, check=False)
        if upstream.returncode:
            print("No upstream branch is configured.")
            return 1
        remote = upstream.stdout.strip()
        if old == remote:
            print("Hermes Privacy Stack is up to date.")
            return 0
        counts = git("rev-list", "--left-right", "--count", f"{old}...{remote}", capture=True).stdout.strip()
        print(f"Update available. local...upstream counts: {counts}")
        return 0

    if shutil.which("hermes"):
        print("Taking Hermes' native quick backup before stack changes...")
        run(["hermes", "backup", "--quick", "--label", "hps-pre-update"], check=False)

    pre = run([sys.executable, str(ROOT / "scripts" / "doctor.py"), "--static"], check=False)
    if pre.returncode:
        raise SystemExit("Pre-update static diagnostics failed. Fix the current install before updating.")

    git("pull", "--ff-only")
    new = git("rev-parse", "HEAD", capture=True).stdout.strip()
    print(f"Repository updated: {old[:12]} -> {new[:12]}")

    post = run([sys.executable, str(ROOT / "bootstrap.py"), "--self-test"], check=False)
    post2 = run([sys.executable, str(ROOT / "scripts" / "doctor.py"), "--static"], check=False)
    if post.returncode or post2.returncode:
        if args.no_rollback:
            raise SystemExit("Post-update validation failed; automatic rollback was disabled.")
        print("Post-update validation failed. Restoring previous repository commit...")
        git("reset", "--hard", old)
        raise SystemExit("Repository rolled back. Services were not changed.")

    if args.services:
        if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
            state_dir = Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
        elif os.name == "nt":
            state_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
        else:
            state_dir = Path.home() / ".hermes-privacy-stack-state"
        state_env = state_dir / "stack.env"
        if state_env.exists() and shutil.which("docker"):
            base = ["docker", "compose", "--env-file", str(state_env), "-f", str(ROOT / "stack" / "compose.yml"), "--profile", "core"]
            run(base + ["pull"])
            run(base + ["up", "-d"])
        else:
            print("! Service update skipped: Docker or generated stack.env not found.")

    if args.hermes:
        if not shutil.which("hermes"):
            print("! --hermes requested but Hermes is not on PATH.")
        else:
            run(["hermes", "update", "--backup"])

    print("Update complete. Run `python scripts/doctor.py` for live service checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
