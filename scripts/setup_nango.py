#!/usr/bin/env python3
"""Configure and optionally start Nango Free Self-Hosted for Hermes Privacy Stack.

This script never asks for third-party OAuth client secrets. It generates only local
runtime secrets (DB password, dashboard password, encryption key) and stores them in
the stack state directory outside Git. Provider OAuth credentials are configured later
inside Nango itself.

Free self-hosted Nango is intentionally treated as an Auth + Proxy boundary. Functions,
webhooks, Nango's managed MCP server, and the full runtime are not assumed here.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = os.name == "nt"


def state_home() -> Path:
    if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
        return Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
    return Path.home() / ".hermes-privacy-stack-state"


def hermes_home() -> Path:
    if os.environ.get("HERMES_HOME"):
        return Path(os.environ["HERMES_HOME"]).expanduser()
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
    return Path.home() / ".hermes"


def atomic_write(path: Path, content: str, private: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    if private and not IS_WINDOWS:
        try:
            os.chmod(path, 0o600)
            os.chmod(path.parent, 0o700)
        except OSError:
            pass


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def set_env(path: Path, key: str, value: str, *, only_if_missing: bool = False) -> str:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    current: str | None = None
    out: list[str] = []
    found = False
    for line in lines:
        if line.startswith(key + "="):
            found = True
            current = line.split("=", 1)[1]
            out.append(line if only_if_missing and current else f"{key}={value}")
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
        current = value
    elif not (only_if_missing and current):
        current = value
    atomic_write(path, "\n".join(out).rstrip() + "\n")
    return current or value


def load_install_state() -> dict:
    path = state_home() / "install.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def validate_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must be http:// or https:// with a hostname.")
    if parsed.username or parsed.password:
        raise ValueError("Do not embed credentials in Nango URLs.")
    if parsed.fragment:
        raise ValueError("Nango base URL must not contain a fragment.")
    return value.rstrip("/")


def default_server_url(bind_address: str) -> str:
    if bind_address in {"127.0.0.1", "localhost"}:
        return "http://localhost:3003"
    return f"http://{bind_address}:3003"


def default_connect_url(server_url: str) -> str:
    parsed = urlsplit(server_url)
    if parsed.scheme == "https":
        return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")
    host = parsed.hostname or "localhost"
    return f"http://{host}:3009"


def ensure_nango_runtime(server_url: str, connect_url: str) -> dict[str, str]:
    env_path = state_home() / "stack.env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if not IS_WINDOWS:
        try:
            os.chmod(env_path.parent, 0o700)
        except OSError:
            pass

    encryption_key = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    db_password = secrets.token_hex(24)
    dashboard_password = secrets.token_urlsafe(24)

    set_env(env_path, "HPS_NANGO_ENCRYPTION_KEY", encryption_key, only_if_missing=True)
    set_env(env_path, "HPS_NANGO_DB_PASSWORD", db_password, only_if_missing=True)
    set_env(env_path, "HPS_NANGO_DASHBOARD_USERNAME", "hps-admin", only_if_missing=True)
    set_env(env_path, "HPS_NANGO_DASHBOARD_PASSWORD", dashboard_password, only_if_missing=True)
    set_env(env_path, "HPS_NANGO_SERVER_URL", server_url)
    set_env(env_path, "HPS_NANGO_CONNECT_URL", connect_url)
    return read_env(env_path)


def mark_profile_enabled() -> None:
    path = state_home() / "install.json"
    state = load_install_state()
    profiles = list(state.get("compose_profiles") or [])
    if "nango" not in profiles:
        profiles.append("nango")
    state["compose_profiles"] = profiles
    state["nango_url"] = read_env(state_home() / "stack.env").get("HPS_NANGO_SERVER_URL")
    state["schema"] = max(int(state.get("schema") or 0), 3)
    atomic_write(path, json.dumps(state, indent=2) + "\n")


def install_skill() -> None:
    source = ROOT / "skills" / "nango-proxy" / "SKILL.md"
    target = hermes_home() / "skills" / "nango-proxy" / "SKILL.md"
    if target.exists():
        print(f"ℹ Nango proxy skill already exists: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"✓ Installed Nango proxy skill: {target}")


def docker_compose(env_path: Path) -> list[str]:
    return [
        "docker",
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        str(ROOT / "stack" / "compose.yml"),
        "--profile",
        "nango",
    ]


def start_nango() -> None:
    if not shutil.which("docker"):
        raise SystemExit("Docker is required to start Nango.")
    info = subprocess.run(["docker", "info"], text=True, capture_output=True)
    if info.returncode:
        raise SystemExit("Docker is installed but its daemon is unavailable.")
    env_path = state_home() / "stack.env"
    cmd = docker_compose(env_path)
    print("+", " ".join(cmd + ["config", "--quiet"]))
    subprocess.run(cmd + ["config", "--quiet"], check=True)
    print("+", " ".join(cmd + ["up", "-d", "nango-db", "nango"]))
    subprocess.run(cmd + ["up", "-d", "nango-db", "nango"], check=True)


def show_credentials() -> int:
    values = read_env(state_home() / "stack.env")
    required = ["HPS_NANGO_DASHBOARD_USERNAME", "HPS_NANGO_DASHBOARD_PASSWORD", "HPS_NANGO_SERVER_URL"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        print("Nango runtime credentials are not configured. Run setup_nango.py first.", file=sys.stderr)
        return 1
    print(f"Nango URL: {values['HPS_NANGO_SERVER_URL']}")
    print(f"Dashboard username: {values['HPS_NANGO_DASHBOARD_USERNAME']}")
    print(f"Dashboard password: {values['HPS_NANGO_DASHBOARD_PASSWORD']}")
    print("Treat the password above as sensitive. It is stored only in the local stack state file.")
    return 0


def self_test() -> int:
    assert default_server_url("127.0.0.1") == "http://localhost:3003"
    assert default_server_url("100.64.1.2") == "http://100.64.1.2:3003"
    assert default_connect_url("http://localhost:3003") == "http://localhost:3009"
    assert default_connect_url("https://nango.example.com") == "https://nango.example.com"
    for valid in ("http://localhost:3003", "https://nango.example.com", "http://100.64.1.2:3003"):
        assert validate_url(valid) == valid.rstrip("/")
    for invalid in ("ftp://example.com", "https://user:pass@example.com", "not-a-url"):
        try:
            validate_url(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe/invalid URL accepted: {invalid}")

    with tempfile.TemporaryDirectory(prefix="hps-nango-test-") as td:
        env = Path(td) / "stack.env"
        first = set_env(env, "HPS_NANGO_DB_PASSWORD", "one", only_if_missing=True)
        second = set_env(env, "HPS_NANGO_DB_PASSWORD", "two", only_if_missing=True)
        assert first == "one" and second == "one"
        assert read_env(env)["HPS_NANGO_DB_PASSWORD"] == "one"
    print("Nango setup pure self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure Nango Free Self-Hosted for Hermes Privacy Stack")
    parser.add_argument("--server-url", help="NANGO_SERVER_URL / OAuth callback base. Defaults to the current stack bind.")
    parser.add_argument("--connect-url", help="Public/base URL for Nango Connect UI.")
    parser.add_argument("--no-start", action="store_true", help="Generate private runtime config but do not start containers.")
    parser.add_argument("--no-install-skill", action="store_true", help="Do not install the local Nango proxy Hermes skill.")
    parser.add_argument("--show-credentials", action="store_true", help="Print locally stored dashboard credentials and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run pure validation without Docker.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.show_credentials:
        return show_credentials()

    state = load_install_state()
    role = str(state.get("role") or "local")
    if role == "client":
        raise SystemExit("Client role does not host Nango. Configure a remote Nango endpoint instead.")

    bind_address = str(state.get("bind_address") or "127.0.0.1")
    server_url = validate_url(args.server_url or default_server_url(bind_address))
    connect_url = validate_url(args.connect_url or default_connect_url(server_url))

    ensure_nango_runtime(server_url, connect_url)
    mark_profile_enabled()
    if not args.no_install_skill:
        install_skill()

    print("✓ Nango runtime secrets generated/preserved outside Git.")
    print(f"  API/dashboard: {server_url}")
    print(f"  Connect UI:    {connect_url}")
    print(f"  Runtime env:   {state_home() / 'stack.env'}")
    print("  Dashboard credentials are not printed by default.")
    print(f"  To reveal them locally: {sys.executable} {Path(__file__).name} --show-credentials")

    if server_url.startswith("http://") and "localhost" not in server_url and "127.0.0.1" not in server_url:
        print("! OAuth providers commonly require an HTTPS callback domain.")
        print("  Before production OAuth, place Nango behind a trusted HTTPS ingress and rerun with --server-url.")

    if not args.no_start:
        start_nango()
        print("✓ Nango Free Self-Hosted started.")
    else:
        print("Nango containers were not started (--no-start).")

    print("\nNext:")
    print("1. Open the Nango dashboard and configure an integration with your own OAuth client where appropriate.")
    print("2. Create a Nango API key scoped to environment:proxy.")
    print("3. Store that key as NANGO_PROXY_TOKEN in your local Hermes .env (never in Git).")
    print("4. Test a read through scripts/nango_proxy.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
