#!/usr/bin/env python3
"""Configure Hermes to use an existing Hindsight server without touching secrets."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def hermes_home() -> Path:
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    return Path.home() / ".hermes"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8888")
    p.add_argument("--bank-template", default="hermes-{profile}")
    p.add_argument("--recall-budget", choices=["low", "mid", "high"], default="mid")
    p.add_argument("--no-activate", action="store_true", help="Write provider config but do not change Hermes' active memory provider.")
    a = p.parse_args()

    if not a.url.startswith(("http://", "https://")):
        raise SystemExit("--url must start with http:// or https://")

    h = hermes_home()
    d = h / "hindsight"
    cfg = {
        "mode": "local_external",
        "api_url": a.url.rstrip("/"),
        "bank_id": "hermes",
        "bank_id_template": a.bank_template,
        "recall_budget": a.recall_budget,
        "memory_mode": "hybrid",
        "auto_retain": True,
        "auto_recall": True,
        "retain_async": True,
        "retain_source": "hermes-privacy-stack",
    }
    atomic_write(d / "config.json", json.dumps(cfg, indent=2) + "\n")

    if not a.no_activate:
        try:
            subprocess.run(["hermes", "config", "set", "memory.provider", "hindsight"], check=False)
        except FileNotFoundError:
            pass

    print(d / "config.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
