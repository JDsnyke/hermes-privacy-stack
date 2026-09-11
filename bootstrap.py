#!/usr/bin/env python3
"""Strict-free, privacy-first bootstrap for Hermes Privacy Stack v2.

Rules:
- Every bundled service is self-hosted and fully usable without paid feature unlocks.
- OAuth/API credentials are never requested by this repository.
- Local services bind to loopback by default; server mode accepts only exact private IPs.
- Runtime secrets/config live outside Git.
- Podman Compose is preferred; Docker Compose remains a compatibility fallback.
- Local llama.cpp is the default model path; ChatGPT/Codex OAuth remains optional.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def _safe_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(errors="replace")
            except (AttributeError, OSError, ValueError):
                pass


_safe_console()
ROOT = Path(__file__).resolve().parent
IS_WINDOWS = os.name == "nt"

if os.environ.get("HERMES_HOME"):
    HERMES_HOME = Path(os.environ["HERMES_HOME"]).expanduser()
elif IS_WINDOWS:
    HERMES_HOME = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes"
else:
    HERMES_HOME = Path.home() / ".hermes"

if os.environ.get("HERMES_PRIVACY_STACK_STATE"):
    STATE = Path(os.environ["HERMES_PRIVACY_STACK_STATE"]).expanduser()
elif IS_WINDOWS:
    STATE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "hermes-privacy-stack"
else:
    STATE = Path.home() / ".hermes-privacy-stack-state"

STACK_ENV = STATE / "stack.env"
RUNTIME = STATE / "runtime"


def run(cmd: Iterable[str] | str, check: bool = True, shell: bool = False, capture: bool = False):
    printable = cmd if isinstance(cmd, str) else " ".join(map(str, cmd))
    print("+", printable)
    return subprocess.run(cmd, check=check, shell=shell, text=True, capture_output=capture)


def command(name: str) -> str | None:
    return shutil.which(name)


def yesno(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n] " if default else " [y/N] "
    ans = input(prompt + suffix).strip().lower()
    return default if not ans else ans in {"y", "yes"}


def choose(prompt: str, options: list[str], default: int) -> str:
    print(f"\n{prompt}")
    for i, item in enumerate(options, 1):
        print(f"  {i}. {item}")
    raw = input(f"Choice [{default}]: ").strip()
    if not raw:
        return options[default - 1]
    try:
        return options[int(raw) - 1]
    except (ValueError, IndexError):
        raise SystemExit("Invalid choice")


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if not IS_WINDOWS:
        try:
            os.chmod(path, 0o700)
        except OSError:
            pass


def atomic_write(path: Path, content: str, private: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    if private and not IS_WINDOWS:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def read_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.lstrip().startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        out[key] = value
    return out


def write_env_var(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out: list[str] = []
    found = False
    for line in lines:
        if line.startswith(key + "="):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
    atomic_write(path, "\n".join(out).rstrip() + "\n", private=True)


def install_hermes(non_interactive: bool = False) -> None:
    if command("hermes"):
        print("✓ Hermes already installed")
        return
    if not non_interactive and not yesno("Install Hermes with the official Nous Research installer?", True):
        return
    if IS_WINDOWS:
        ps = command("pwsh") or command("powershell")
        if not ps:
            raise SystemExit("PowerShell is required to install Hermes on Windows.")
        run([ps, "-NoProfile", "-Command", "iex (irm https://hermes-agent.nousresearch.com/install.ps1)"])
    else:
        run(["bash", "-lc", "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"])


def validate_private_bind(value: str) -> str:
    raw = value.strip().split("/", 1)[0]
    if raw in {"0.0.0.0", "::", "*", ""}:
        raise ValueError("Wildcard/empty bind addresses are not allowed.")
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError as exc:
        raise ValueError("Bind address must be an IP address.") from exc
    if ip.version != 4:
        raise ValueError("Server binding currently requires IPv4.")
    cgnat = ipaddress.ip_network("100.64.0.0/10")
    if not (ip.is_loopback or ip.is_private or ip.is_link_local or ip in cgnat):
        raise ValueError(f"{raw} is globally routable; refusing to expose the stack.")
    return raw


def select_bind_address(role: str, supplied: str | None, non_interactive: bool) -> str:
    if role == "client":
        return "127.0.0.1"
    if role == "local":
        return validate_private_bind(supplied or "127.0.0.1")
    if supplied:
        return validate_private_bind(supplied)
    if non_interactive:
        raise SystemExit("Server role requires --bind-address pointing to a Headscale/WireGuard/private LAN IPv4.")
    while True:
        raw = input("Private Headscale/WireGuard/LAN IPv4 for server services: ").strip()
        try:
            return validate_private_bind(raw)
        except ValueError as exc:
            print(f"! {exc}")


def detect_runtime() -> tuple[str, list[str]] | None:
    # Prefer the completely free/open Podman stack. Docker Compose remains a
    # compatibility fallback for users who already have a suitable Docker Engine.
    if command("podman"):
        info = run(["podman", "info"], check=False, capture=True)
        compose = run(["podman", "compose", "version"], check=False, capture=True)
        if info.returncode == 0 and compose.returncode == 0:
            return "podman", ["podman", "compose"]
    if command("docker"):
        info = run(["docker", "info"], check=False, capture=True)
        compose = run(["docker", "compose", "version"], check=False, capture=True)
        if info.returncode == 0 and compose.returncode == 0:
            return "docker", ["docker", "compose"]
    return None


def ensure_runtime_searxng() -> Path:
    runtime_dir = RUNTIME / "searxng"
    ensure_private_dir(runtime_dir)
    target = runtime_dir / "settings.yml"
    template = ROOT / "stack" / "config" / "searxng" / "settings.yml"
    if target.exists():
        return runtime_dir
    content = template.read_text(encoding="utf-8")
    marker = "__HPS_SEARXNG_SECRET__"
    if marker not in content:
        raise SystemExit(f"SearXNG template is missing {marker}.")
    atomic_write(target, content.replace(marker, secrets.token_hex(32)), private=True)
    return runtime_dir


def write_stack_env(bind_address: str, searxng_config: Path, llama_model: Path | None) -> dict[str, str]:
    ensure_private_dir(STATE)
    existing = read_env(STACK_ENV)
    values = dict(existing)
    values["HPS_BIND_ADDRESS"] = bind_address
    values["HPS_SEARXNG_CONFIG_DIR"] = searxng_config.resolve().as_posix()
    values.setdefault("HPS_MEMORY_API_KEY", secrets.token_urlsafe(48))
    values.setdefault("HPS_NODERED_CREDENTIAL_SECRET", secrets.token_urlsafe(48))
    if llama_model:
        model = llama_model.expanduser().resolve()
        if not model.is_file() or model.suffix.lower() != ".gguf":
            raise SystemExit(f"Local model must be an existing .gguf file: {model}")
        values["HPS_LLAMA_MODEL_DIR"] = model.parent.as_posix()
        values["HPS_LLAMA_MODEL_FILE"] = model.name
    atomic_write(STACK_ENV, "\n".join(f"{k}={v}" for k, v in sorted(values.items())) + "\n", private=True)
    return values


def compose_base(compose_cmd: list[str]) -> list[str]:
    return compose_cmd + ["--env-file", str(STACK_ENV), "-f", str(ROOT / "stack" / "compose.yml")]


def requested_profiles(preset: str, model_provider: str, non_interactive: bool) -> list[str]:
    if preset == "minimal":
        profiles: list[str] = []
    else:
        profiles = ["core"]
    if preset in {"balanced", "developer"} and (non_interactive or yesno("Enable local Crawl4AI research service?", True)):
        profiles.append("research")
    if preset == "developer":
        if non_interactive or yesno("Enable Node-RED automation?", True):
            profiles.append("automation")
        if non_interactive or yesno("Enable private Forgejo Git service?", False):
            profiles.append("git")
    if model_provider == "local":
        profiles.append("local-model")
    return profiles


def start_stack(compose_cmd: list[str], profiles: list[str], bind_address: str) -> None:
    if not profiles:
        print("No local service profiles selected.")
        return
    args = compose_base(compose_cmd)
    for profile in profiles:
        args += ["--profile", profile]
    run(args + ["config", "--quiet"])
    run(args + ["up", "-d"])
    print(f"✓ Self-hosted services started on {bind_address}: {', '.join(profiles)}")


def snapshot_hermes() -> None:
    if command("hermes") and (HERMES_HOME / "config.yaml").exists():
        run(["hermes", "backup", "--quick", "--label", "hps-v2-preconfigure"], check=False)


def hermes_config_set(key: str, value: str) -> None:
    if command("hermes"):
        run(["hermes", "config", "set", key, value], check=False)


def configure_web(searxng_url: str) -> None:
    write_env_var(HERMES_HOME / ".env", "SEARXNG_URL", searxng_url.rstrip("/"))
    hermes_config_set("web.search_backend", "searxng")
    hermes_config_set("web.keyless_fallback", "false")
    hermes_config_set("web.keyless_rescue", "false")


def configure_memory_mcp(memory_url: str, memory_key: str) -> None:
    write_env_var(HERMES_HOME / ".env", "MCP_MEMORY_API_KEY", memory_key)
    endpoint = memory_url.rstrip("/") + "/mcp"
    hermes_config_set("mcp_servers.memory.url", endpoint)
    hermes_config_set("mcp_servers.memory.headers.Authorization", "Bearer ${MCP_MEMORY_API_KEY}")
    hermes_config_set("mcp_servers.memory.tools.resources", "false")
    hermes_config_set("mcp_servers.memory.tools.prompts", "false")
    print(f"✓ Shared memory MCP configured at {endpoint}")


def configure_local_model(bind_address: str, model_file: Path) -> None:
    base_url = f"http://{bind_address}:8080/v1"
    hermes_config_set("model.provider", "custom")
    hermes_config_set("model.base_url", base_url)
    hermes_config_set("model.default", model_file.stem)
    hermes_config_set("model.api_key", "local")
    print(f"✓ Hermes local model endpoint configured at {base_url}")


def seed_templates(non_interactive: bool = False) -> None:
    HERMES_HOME.mkdir(parents=True, exist_ok=True)
    soul = HERMES_HOME / "SOUL.md"
    if not soul.exists() and (non_interactive or yesno("Install privacy-first starter SOUL.md?", True)):
        atomic_write(soul, (ROOT / "profile" / "SOUL.md").read_text(encoding="utf-8"))
    user = HERMES_HOME / "USER.md"
    if not user.exists():
        atomic_write(user, "# User\n\nLocal-only durable context. Never place secrets here.\n", private=True)


def resolve_url(value: str | None, label: str, non_interactive: bool, example: str) -> str:
    if value:
        return value.rstrip("/")
    if non_interactive:
        raise SystemExit(f"{label} is required for client role.")
    while True:
        raw = input(f"{label} (e.g. {example}): ").strip().rstrip("/")
        if raw.startswith(("http://", "https://")):
            return raw
        print("! Enter an http:// or https:// URL reachable only through your trusted network.")


def choose_model_provider(arg_value: str | None, non_interactive: bool) -> str:
    if arg_value:
        return arg_value
    if non_interactive:
        return "skip"
    picked = choose(
        "Model provider",
        [
            "local — llama.cpp on your own hardware (strict-free default)",
            "chatgpt-oauth — optional ChatGPT/Codex OAuth through Hermes",
            "skip — configure a model later",
        ],
        1,
    )
    return picked.split(" —", 1)[0]


def resolve_llama_model(value: str | None, non_interactive: bool) -> Path:
    if value:
        return Path(value).expanduser()
    if non_interactive:
        raise SystemExit("--llama-model is required with --model-provider local in non-interactive mode.")
    raw = input("Path to a local GGUF model (Hermes needs >=64K context support): ").strip()
    if not raw:
        raise SystemExit("A GGUF path is required for local llama.cpp mode.")
    return Path(raw).expanduser()


def save_state(preset: str, role: str, bind: str, runtime: str | None, memory_url: str, searxng_url: str, profiles: list[str], model_provider: str) -> None:
    ensure_private_dir(STATE)
    payload = {
        "schema": 4,
        "architecture": "strict-free-v2",
        "preset": preset,
        "role": role,
        "platform": platform.platform(),
        "bind_address": bind,
        "container_runtime": runtime,
        "memory_url": memory_url,
        "searxng_url": searxng_url,
        "compose_profiles": profiles,
        "model_provider": model_provider,
    }
    atomic_write(STATE / "install.json", json.dumps(payload, indent=2) + "\n", private=True)


def self_test() -> None:
    for candidate in ["127.0.0.1", "192.168.1.20", "10.0.0.2", "172.16.1.4", "100.64.0.1"]:
        validate_private_bind(candidate)
    for rejected in ["0.0.0.0", "::", "8.8.8.8", "1.1.1.1"]:
        try:
            validate_private_bind(rejected)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe bind accepted: {rejected}")
    print("bootstrap strict-free v2 self-test passed")


def main() -> int:
    ap = argparse.ArgumentParser(description="Install/configure Hermes Privacy Stack strict-free v2")
    ap.add_argument("--preset", choices=["strict", "balanced", "developer", "minimal"])
    ap.add_argument("--role", choices=["local", "server", "client"])
    ap.add_argument("--bind-address")
    ap.add_argument("--memory-url", help="Existing mcp-memory-service base URL for client role")
    ap.add_argument("--searxng-url", help="Existing SearXNG URL for client role")
    ap.add_argument("--model-provider", choices=["local", "chatgpt-oauth", "skip"])
    ap.add_argument("--llama-model", help="Path to a local GGUF file when using llama.cpp")
    ap.add_argument("--non-interactive", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ required")
    if args.self_test:
        self_test()
        return 0

    print("\nHermes Privacy Stack v2 — strict-free, local-first, no paid service unlocks\n")
    preset = args.preset or ("balanced" if args.non_interactive else choose("Preset", ["strict", "balanced", "developer", "minimal"], 2))
    role = args.role or ("local" if args.non_interactive else choose("Machine role", ["local", "server", "client"], 1))
    model_provider = choose_model_provider(args.model_provider, args.non_interactive)
    llama_model = resolve_llama_model(args.llama_model, args.non_interactive) if model_provider == "local" else None

    install_hermes(args.non_interactive)
    snapshot_hermes()
    seed_templates(args.non_interactive)
    bind = select_bind_address(role, args.bind_address, args.non_interactive)

    runtime_name: str | None = None
    profiles: list[str] = []
    if role == "client":
        memory_url = resolve_url(args.memory_url, "--memory-url", args.non_interactive, "http://100.64.0.10:8765")
        searxng_url = resolve_url(args.searxng_url, "--searxng-url", args.non_interactive, "http://100.64.0.10:8088")
        memory_key = os.environ.get("MCP_MEMORY_API_KEY", "")
        if not memory_key:
            raise SystemExit("Client role requires MCP_MEMORY_API_KEY in the process environment; it is never accepted as a CLI argument.")
    else:
        searx_dir = ensure_runtime_searxng()
        values = write_stack_env(bind, searx_dir, llama_model)
        memory_key = values["HPS_MEMORY_API_KEY"]
        memory_url = f"http://{bind}:8765"
        searxng_url = f"http://{bind}:8088"
        detected = detect_runtime()
        if detected:
            runtime_name, compose_cmd = detected
            profiles = requested_profiles(preset, model_provider, args.non_interactive)
            start_stack(compose_cmd, profiles, bind)
        else:
            print("! No working Podman Compose or Docker Compose runtime found. Hermes configuration will still be written.")
            profiles = requested_profiles(preset, model_provider, True)

    configure_memory_mcp(memory_url, memory_key)
    configure_web(searxng_url)
    if model_provider == "local" and llama_model is not None:
        configure_local_model(bind, llama_model)
    elif model_provider == "chatgpt-oauth":
        if command("hermes") and not args.non_interactive:
            print("\nOpening Hermes model wizard. Choose OpenAI Codex / ChatGPT OAuth.")
            run(["hermes", "model"], check=False)
        else:
            print("\nOptional ChatGPT OAuth selected. Run `hermes model` and choose OpenAI Codex / ChatGPT OAuth.")

    save_state(preset, role, bind, runtime_name, memory_url, searxng_url, profiles, model_provider)
    if command("hermes"):
        run(["hermes", "config", "check"], check=False)

    print("\n✓ Strict-free v2 bootstrap complete")
    print(f"Diagnostics: python {ROOT / 'scripts' / 'doctor.py'}")
    print("Core software: Hermes + mcp-memory-service + SearXNG + Docling")
    print("Optional free profiles: llama.cpp, Crawl4AI, Node-RED, Forgejo")
    print("Private networking: Headscale or plain WireGuard; paid/open-core overlays are intentionally excluded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
