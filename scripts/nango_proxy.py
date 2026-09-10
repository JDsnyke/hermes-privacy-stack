#!/usr/bin/env python3
"""Least-authority CLI wrapper around Nango's authenticated Proxy API.

Read-only requests (GET/HEAD) are allowed by default. State-changing methods require
--allow-write so an agent cannot turn a generic Nango connection into silent write
authority merely by discovering this helper.

The Nango API token is never accepted as a command-line argument. Supply
NANGO_PROXY_TOKEN via the process environment or the local Hermes .env file.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

IS_WINDOWS = os.name == "nt"
READ_ONLY = {"GET", "HEAD"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


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


def load_env_file(path: Path) -> dict[str, str]:
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


def resolve_setting(name: str, *files: Path) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    for path in files:
        value = load_env_file(path).get(name)
        if value:
            return value
    return None


def validate_base_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Nango base URL must be http:// or https:// with a hostname.")
    if parsed.username or parsed.password:
        raise ValueError("Do not embed credentials in the Nango URL.")
    return value.rstrip("/")


def normalize_proxy_path(value: str) -> str:
    if "://" in value:
        raise ValueError("Pass only the provider API path, not an absolute URL.")
    if not value.startswith("/"):
        value = "/" + value
    if value.startswith("//"):
        raise ValueError("Proxy path must not be protocol-relative.")
    return value


def body_bytes(body: str | None, body_file: str | None) -> bytes | None:
    if body and body_file:
        raise ValueError("Use only one of --body or --body-file.")
    if body_file:
        body = Path(body_file).read_text(encoding="utf-8")
    if body is None:
        return None
    parsed = json.loads(body)
    return json.dumps(parsed, separators=(",", ":")).encode("utf-8")


def self_test() -> int:
    assert normalize_proxy_path("v1/me") == "/v1/me"
    assert normalize_proxy_path("/v1/me?x=1") == "/v1/me?x=1"
    try:
        normalize_proxy_path("https://evil.example/path")
    except ValueError:
        pass
    else:
        raise AssertionError("absolute URL accepted as proxy path")
    assert validate_base_url("http://localhost:3003") == "http://localhost:3003"
    assert body_bytes('{"a": 1}', None) == b'{"a":1}'
    print("Nango proxy pure self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Call an external API through Nango's credential proxy")
    parser.add_argument("--provider", required=False, help="Nango Provider-Config-Key / integration ID")
    parser.add_argument("--connection", required=False, help="Nango Connection-Id")
    parser.add_argument("--path", required=False, help="External provider API path, e.g. /user")
    parser.add_argument("--method", choices=sorted(READ_ONLY | WRITE_METHODS), default="GET")
    parser.add_argument("--body", help="JSON request body")
    parser.add_argument("--body-file", help="Path to a JSON request body")
    parser.add_argument("--allow-write", action="store_true", help="Required for POST/PUT/PATCH/DELETE")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    missing_args = [name for name, value in (
        ("--provider", args.provider),
        ("--connection", args.connection),
        ("--path", args.path),
    ) if not value]
    if missing_args:
        parser.error("missing required arguments: " + ", ".join(missing_args))

    method = args.method.upper()
    if method in WRITE_METHODS and not args.allow_write:
        raise SystemExit(
            f"{method} is state-changing. Refusing request without --allow-write. "
            "Obtain explicit user approval before retrying."
        )

    hermes_env = hermes_home() / ".env"
    stack_env = state_home() / "stack.env"
    token = resolve_setting("NANGO_PROXY_TOKEN", hermes_env)
    if not token:
        raise SystemExit(
            f"NANGO_PROXY_TOKEN is missing. Store a Nango API key scoped to environment:proxy "
            f"in {hermes_env}; never commit it."
        )

    base = resolve_setting("NANGO_HOSTPORT", hermes_env) or resolve_setting("HPS_NANGO_SERVER_URL", stack_env)
    if not base:
        base = "http://localhost:3003"
    base = validate_base_url(base)
    path = normalize_proxy_path(args.path)
    data = body_bytes(args.body, args.body_file)

    headers = {
        "Authorization": f"Bearer {token}",
        "Provider-Config-Key": args.provider,
        "Connection-Id": args.connection,
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = Request(base + "/proxy" + path, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=args.timeout) as response:
            payload = response.read()
            if method != "HEAD":
                sys.stdout.buffer.write(payload)
                if payload and not payload.endswith(b"\n"):
                    sys.stdout.buffer.write(b"\n")
            print(f"Nango proxy status: {response.status}", file=sys.stderr)
            return 0 if 200 <= response.status < 400 else 1
    except HTTPError as exc:
        payload = exc.read()
        if payload:
            sys.stderr.buffer.write(payload)
            if not payload.endswith(b"\n"):
                sys.stderr.buffer.write(b"\n")
        print(f"Nango proxy HTTP error: {exc.code}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Nango proxy connection error: {exc.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
