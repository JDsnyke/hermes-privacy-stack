#!/usr/bin/env python3
"""Diagnostics for Hermes Privacy Stack.

Default output is human-readable. `--json --redact` is suitable for a support
bundle after the user reviews it. No credentials or file contents are emitted.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
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
    parser.add_argument("--static", action="store_true", help="Skip network/service probes; useful in CI.")
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
            add("install-state", True, str(state_file))
        except Exception as exc:
            add("install-state", False, f"{state_file}: {exc}")
    else:
        add("install-state", False, f"not found: {state_file}", required=not args.static)

    role = str(state.get("role", "local"))
    profiles = set(state.get("compose_profiles") or [])
    hindsight_url = str(state.get("hindsight_url") or "http://127.0.0.1:8888").rstrip("/")
    searxng_url = str(state.get("searxng_url") or "http://127.0.0.1:8088").rstrip("/")
    nango_url = str(state.get("nango_url") or "http://127.0.0.1:3003").rstrip("/")
    bind_address = str(state.get("bind_address") or "127.0.0.1")

    for cmd, required in [("git", True), ("hermes", not args.static), ("docker", role != "client" and not args.static)]:
        location = shutil.which(cmd)
        add(cmd, bool(location), location or "not found", required=required)
    add("python", sys.version_info >= (3, 10), sys.version.split()[0])

    hcfg = hermes_home / "hindsight" / "config.json"
    if hcfg.exists():
        try:
            cfg = json.loads(hcfg.read_text(encoding="utf-8"))
            ok = cfg.get("mode") == "local_external" and cfg.get("bank_id_template") == "hermes-{profile}"
            if state:
                ok = ok and str(cfg.get("api_url", "")).rstrip("/") == hindsight_url
            add("hindsight-config", ok, str(hcfg), required=not args.static)
        except Exception as exc:
            add("hindsight-config", False, f"{hcfg}: {exc}", required=not args.static)
    else:
        add("hindsight-config", False, f"not found: {hcfg}", required=not args.static)

    if shutil.which("hermes") and not args.static:
        expected = {
            "memory.provider": "hindsight",
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

    if role == "server":
        try:
            import ipaddress
            ip = ipaddress.ip_address(bind_address)
            safe = ip.is_private or ip.is_loopback or ip.is_link_local or (ip.version == 4 and ip in ipaddress.ip_network("100.64.0.0/10"))
            add("server-bind", safe and bind_address not in {"0.0.0.0", "::"}, bind_address)
        except Exception as exc:
            add("server-bind", False, str(exc))

    def http(name: str, url: str, required: bool = True) -> None:
        display = redact_url(url) if args.redact else url
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hermes-privacy-stack-doctor/1"})
            with urllib.request.urlopen(req, timeout=5) as response:
                add(name, 200 <= response.status < 500, f"HTTP {response.status} {display}", required)
        except Exception as exc:
            detail = f"{display}: {type(exc).__name__}" if args.redact else f"{display}: {exc}"
            add(name, False, detail, required)

    if not args.static:
        http("Hindsight", hindsight_url + "/health")
        query = urllib.parse.urlencode({"q": "privacy test", "format": "json"})
        http("SearXNG", searxng_url + "/search?" + query)
        if role != "client":
            scheme_host = f"http://{bind_address}"
            http("Docling", scheme_host + ":5001/docs", required=False)
            if "automation" in profiles:
                http("Activepieces", scheme_host + ":8090/", required=False)
            if "nango" in profiles:
                # Nango's /health route is intentionally unauthenticated upstream, so
                # diagnostics do not need to read or expose dashboard/proxy credentials.
                http("Nango", nango_url + "/health", required=False)

    failed_required = [c for c in checks if c["required"] and not c["ok"]]
    if args.json:
        print(json.dumps({"ok": not failed_required, "role": role, "checks": checks}, indent=2))
    else:
        for item in checks:
            symbol = "✓" if item["ok"] else ("!" if not item["required"] else "✗")
            print(symbol, f"{item['name']}: {item['detail']}")
        print(f"\n{sum(c['ok'] for c in checks)}/{len(checks)} checks passed; {len(failed_required)} required failure(s).")
    return 1 if failed_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
