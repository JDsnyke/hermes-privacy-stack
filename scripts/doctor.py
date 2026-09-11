#!/usr/bin/env python3
"""Privacy-safe diagnostics for Hermes Privacy Stack strict-free v2."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

IS_WINDOWS = os.name == "nt"


def paths() -> tuple[Path, Path]:
    if os.environ.get("HERMES_HOME"):
        hermes_home = Path(os.environ["HERMES_HOME"]).expanduser()
    elif IS_WINDOWS:
        hermes_home = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    else:
        hermes_home = Path.home() / ".hermes"
    if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
        state = Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
    elif IS_WINDOWS:
        state = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
    else:
        state = Path.home() / ".hermes-privacy-stack-state"
    return hermes_home, state


def redact_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url)
        if not p.scheme or not p.netloc:
            return url
        port = f":{p.port}" if p.port else ""
        return urllib.parse.urlunsplit((p.scheme, f"<private-host>{port}", p.path, p.query, p.fragment))
    except Exception:
        return "<redacted-url>"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--redact", action="store_true")
    parser.add_argument("--static", action="store_true", help="Skip network/service probes")
    args = parser.parse_args()

    hermes_home, state_dir = paths()
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, required: bool = True) -> None:
        checks.append({"name": name, "ok": bool(ok), "required": required, "detail": detail})

    state_file = state_dir / "install.json"
    state: dict[str, Any] = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            add("install-state", state.get("architecture") == "strict-free-v2", str(state_file))
        except Exception as exc:
            add("install-state", False, f"{state_file}: {exc}")
    else:
        add("install-state", False, f"not found: {state_file}", required=not args.static)

    role = str(state.get("role", "local"))
    profiles = set(state.get("compose_profiles") or [])
    bind = str(state.get("bind_address") or "127.0.0.1")
    memory_url = str(state.get("memory_url") or f"http://{bind}:8765").rstrip("/")
    searxng_url = str(state.get("searxng_url") or f"http://{bind}:8088").rstrip("/")

    add("python", sys.version_info >= (3, 10), sys.version.split()[0])
    add("git", bool(shutil.which("git")), shutil.which("git") or "not found")
    add("hermes", bool(shutil.which("hermes")), shutil.which("hermes") or "not found", required=not args.static)
    podman = shutil.which("podman")
    docker = shutil.which("docker")
    add("container-runtime", bool(podman or docker) or role == "client", podman or docker or "not found", required=role != "client" and not args.static)

    env_file = hermes_home / ".env"
    env_text = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
    add("memory-token-local", "MCP_MEMORY_API_KEY=" in env_text, "present in local Hermes .env" if "MCP_MEMORY_API_KEY=" in env_text else "missing", required=not args.static)

    if shutil.which("hermes") and not args.static:
        expected = {
            "web.search_backend": "searxng",
            "web.keyless_fallback": False,
            "web.keyless_rescue": False,
        }
        for key, want in expected.items():
            try:
                proc = subprocess.run(["hermes", "config", "get", key, "--json"], capture_output=True, text=True, timeout=10, check=False)
                raw = proc.stdout.strip()
                try:
                    got = json.loads(raw)
                except Exception:
                    got = raw
                add(f"config:{key}", proc.returncode == 0 and got == want, f"{got!r} (expected {want!r})")
            except Exception as exc:
                add(f"config:{key}", False, str(exc))

    def http(name: str, url: str, required: bool = True) -> None:
        display = redact_url(url) if args.redact else url
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hermes-privacy-stack-doctor/2"})
            with urllib.request.urlopen(req, timeout=5) as response:
                add(name, 200 <= response.status < 500, f"HTTP {response.status} {display}", required)
        except urllib.error.HTTPError as exc:
            # 4xx from an authenticated MCP endpoint still proves the service is reachable.
            add(name, 400 <= exc.code < 500, f"HTTP {exc.code} {display}", required)
        except Exception as exc:
            add(name, False, f"{display}: {type(exc).__name__ if args.redact else exc}", required)

    if not args.static:
        http("memory-mcp", memory_url + "/mcp")
        query = urllib.parse.urlencode({"q": "privacy test", "format": "json"})
        http("SearXNG", searxng_url + "/search?" + query)
        if role != "client":
            base = f"http://{bind}"
            http("Docling", base + ":5001/docs", required=False)
            if "research" in profiles:
                http("Crawl4AI", base + ":11235/health", required=False)
            if "automation" in profiles:
                http("Node-RED", base + ":1880/", required=False)
            if "git" in profiles:
                http("Forgejo", base + ":3000/", required=False)
            if "local-model" in profiles:
                http("llama.cpp", base + ":8080/v1/models", required=False)

    failed = [c for c in checks if c["required"] and not c["ok"]]
    if args.json:
        print(json.dumps({"ok": not failed, "architecture": "strict-free-v2", "role": role, "checks": checks}, indent=2))
    else:
        for item in checks:
            symbol = "✓" if item["ok"] else ("!" if not item["required"] else "✗")
            print(symbol, f"{item['name']}: {item['detail']}")
        print(f"\n{sum(c['ok'] for c in checks)}/{len(checks)} checks passed; {len(failed)} required failure(s).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
