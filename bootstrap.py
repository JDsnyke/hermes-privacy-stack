#!/usr/bin/env python3
"""Privacy-first cross-platform bootstrap for Hermes Privacy Stack.

Design rules:
- OAuth/API credentials are never requested or stored by this repository.
- Hermes authentication/model selection stays inside Hermes' own CLI.
- Local services bind to loopback by default.
- Server mode rejects wildcard/public binds and accepts only an exact private overlay/LAN address.
- Private networking is provider-agnostic (NetBird, Tailscale/Headscale, WireGuard, etc.).
- Runtime secrets and generated service config live outside the Git checkout.
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


def _make_console_output_lossless_enough() -> None:
    """Prevent status glyphs from crashing CP1252/legacy Windows consoles.

    Keep the terminal's selected encoding rather than forcing UTF-8 globally. When a
    cosmetic character is not representable, replace only that character instead of
    aborting the installer. This also applies when bootstrap.py is imported by tests.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_make_console_output_lossless_enough()

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


def write_env_var(path: Path, key: str, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    if not non_interactive and not yesno("Hermes is not installed. Install it using the official Nous Research installer?", True):
        print("Skipping Hermes installation.")
        return
    if IS_WINDOWS:
        ps = command("pwsh") or command("powershell")
        if not ps:
            raise SystemExit("PowerShell is required to install Hermes on Windows.")
        run([ps, "-NoProfile", "-Command", "iex (irm https://hermes-agent.nousresearch.com/install.ps1)"])
    else:
        run(["bash", "-lc", "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"])


def validate_private_bind(value: str) -> str:
    """Allow exact loopback/private/link-local/CGNAT IPv4; reject wildcard/global addresses."""
    raw = value.strip().split("/", 1)[0]
    if raw in {"0.0.0.0", "::", "*", ""}:
        raise ValueError("Wildcard/empty bind addresses are not allowed by the privacy-first installer.")
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError as exc:
        raise ValueError("Bind address must be an IP address, not a hostname.") from exc
    if ip.version != 4:
        raise ValueError("Server binding currently requires an IPv4 address.")

    cgnat = ipaddress.ip_network("100.64.0.0/10")
    safe = ip.is_loopback or ip.is_private or ip.is_link_local or ip in cgnat
    if not safe:
        raise ValueError(f"{raw} is a globally routable address. Refusing to expose local services.")
    return raw


def _run_overlay_ip(cmd: list[str]) -> str | None:
    if not command(cmd[0]):
        return None
    try:
        proc = run(cmd, check=False, capture=True)
    except Exception:
        return None
    if proc.returncode:
        return None
    for line in proc.stdout.splitlines():
        try:
            return validate_private_bind(line.strip())
        except ValueError:
            continue
    return None


def detect_netbird_ipv4() -> str | None:
    return _run_overlay_ip(["netbird", "status", "--ipv4"])


def detect_tailscale_ipv4() -> str | None:
    # Works for ordinary Tailscale and Tailscale clients enrolled against Headscale.
    return _run_overlay_ip(["tailscale", "ip", "-4"])


def detect_overlay_ipv4(provider: str = "auto") -> tuple[str, str] | None:
    detectors = []
    if provider in {"auto", "netbird"}:
        detectors.append(("netbird", detect_netbird_ipv4))
    if provider in {"auto", "tailscale"}:
        detectors.append(("tailscale-or-headscale", detect_tailscale_ipv4))
    for name, detector in detectors:
        value = detector()
        if value:
            return name, value
    return None


def select_bind_address(role: str, supplied: str | None, non_interactive: bool, network_provider: str) -> tuple[str, str]:
    if role == "client":
        return "127.0.0.1", "client"
    if role == "local":
        return validate_private_bind(supplied or "127.0.0.1"), "local"
    if supplied:
        return validate_private_bind(supplied), network_provider if network_provider != "auto" else "manual"

    # For non-interactive automation, `auto` is intentionally not allowed to pick
    # whichever client happens to be installed. Select a provider or pass --bind-address.
    if non_interactive and network_provider in {"auto", "manual"}:
        raise SystemExit(
            "Non-interactive server role requires --bind-address, or an explicit "
            "--network-provider netbird|tailscale with a connected client."
        )

    if network_provider != "manual":
        detected = detect_overlay_ipv4(network_provider)
        if detected:
            provider, value = detected
            if non_interactive or yesno(f"Bind server services to detected {provider} address {value}?", True):
                return value, provider
        elif network_provider in {"netbird", "tailscale"} and non_interactive:
            raise SystemExit(f"No connected {network_provider} IPv4 address detected.")

    if non_interactive:
        raise SystemExit("--bind-address is required for this server configuration.")

    while True:
        raw = input("Private overlay/LAN IPv4 for server services (never 0.0.0.0): ").strip()
        try:
            return validate_private_bind(raw), "manual"
        except ValueError as exc:
            print(f"! {exc}")


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
        raise SystemExit(f"SearXNG template is missing required marker {marker}.")
    content = content.replace(marker, secrets.token_hex(32))
    atomic_write(target, content, private=True)
    return runtime_dir


def write_stack_env(bind_address: str, searxng_config: Path) -> None:
    ensure_private_dir(STATE)
    values = {
        "HPS_BIND_ADDRESS": bind_address,
        "HPS_SEARXNG_CONFIG_DIR": searxng_config.resolve().as_posix(),
        "HPS_HINDSIGHT_MODEL": os.environ.get("HPS_HINDSIGHT_MODEL", "qwen3.5:4b"),
    }
    atomic_write(STACK_ENV, "\n".join(f"{k}={v}" for k, v in values.items()) + "\n", private=True)


def compose_base() -> list[str]:
    return ["docker", "compose", "--env-file", str(STACK_ENV), "-f", str(ROOT / "stack" / "compose.yml")]


def start_stack(
    preset: str,
    role: str,
    bind_address: str,
    non_interactive: bool = False,
    enable_activepieces: bool = False,
) -> list[str]:
    if role == "client":
        print("Client role: no local service stack started.")
        return []
    if not command("docker"):
        print("! Docker not found. Hermes can still run. Install Docker Desktop/Engine, then rerun the installer.")
        return []
    info = run(["docker", "info"], check=False, capture=True)
    if info.returncode:
        print("! Docker is installed but the daemon is not available.")
        return []

    profiles = ["core"]
    if preset in {"balanced", "developer"}:
        activepieces = enable_activepieces or (
            not non_interactive and yesno("Start optional Activepieces integration service?", False)
        )
        if activepieces:
            profiles.append("automation")
        print("ℹ OpenViking remains opt-in/planned until authenticated runtime config is generated safely.")

    args = compose_base()
    for profile in profiles:
        args += ["--profile", profile]
    run(args + ["config", "--quiet"])
    run(args + ["up", "-d"])
    print(f"✓ Local services started on {bind_address}")
    return profiles


def snapshot_hermes() -> None:
    if not command("hermes") or not (HERMES_HOME / "config.yaml").exists():
        return
    print("Taking a local Hermes pre-configuration snapshot...")
    run(["hermes", "backup", "--quick", "--label", "hps-preconfigure"], check=False)


def hermes_config_set(key: str, value: str) -> None:
    if command("hermes"):
        run(["hermes", "config", "set", key, value], check=False)


def configure_privacy_web(searxng_url: str) -> None:
    write_env_var(HERMES_HOME / ".env", "SEARXNG_URL", searxng_url)
    hermes_config_set("web.search_backend", "searxng")
    hermes_config_set("web.keyless_fallback", "false")
    hermes_config_set("web.keyless_rescue", "false")
    print(f"✓ Privacy web search configured at {searxng_url}")


def configure_hindsight(api_url: str) -> None:
    cfgdir = HERMES_HOME / "hindsight"
    cfgdir.mkdir(parents=True, exist_ok=True)
    api = api_url.rstrip("/")
    cfg = {
        "mode": "local_external",
        "api_url": api,
        "bank_id": "hermes",
        "bank_id_template": "hermes-{profile}",
        "recall_budget": "mid",
        "memory_mode": "hybrid",
        "auto_retain": True,
        "auto_recall": True,
        "retain_async": True,
        "retain_source": "hermes-privacy-stack",
        "retain_indicator": True,
    }
    atomic_write(cfgdir / "config.json", json.dumps(cfg, indent=2) + "\n", private=True)
    write_env_var(HERMES_HOME / ".env", "HINDSIGHT_API_URL", api)
    hermes_config_set("memory.provider", "hindsight")
    print(f"✓ Hindsight configured at {api}")


def seed_templates(non_interactive: bool = False) -> None:
    HERMES_HOME.mkdir(parents=True, exist_ok=True)
    soul = HERMES_HOME / "SOUL.md"
    if not soul.exists() and (non_interactive or yesno("Install the privacy-first starter SOUL.md?", True)):
        atomic_write(soul, (ROOT / "profile" / "SOUL.md").read_text(encoding="utf-8"))
        print("✓ SOUL.md installed")
    user = HERMES_HOME / "USER.md"
    if not user.exists():
        atomic_write(
            user,
            "# User\n\nThis file is intentionally local and is never sourced from Git. "
            "Add only information you want Hermes to retain as durable profile context.\n",
            private=True,
        )
        print("✓ Local USER.md created")


def resolve_client_url(value: str | None, label: str, non_interactive: bool, example: str) -> str:
    if value:
        return value.rstrip("/")
    if non_interactive:
        raise SystemExit(f"{label} is required for non-interactive client role.")
    while True:
        raw = input(f"{label} (e.g. {example}): ").strip().rstrip("/")
        if raw.startswith(("http://", "https://")):
            return raw
        print("! Enter an http:// or https:// URL reachable only through your trusted network.")


def save_install_state(
    preset: str,
    role: str,
    bind_address: str,
    hindsight_url: str,
    searxng_url: str,
    profiles: list[str],
    network_provider: str,
) -> None:
    ensure_private_dir(STATE)
    payload = {
        "schema": 3,
        "preset": preset,
        "role": role,
        "platform": platform.platform(),
        "bind_address": bind_address,
        "network_provider": network_provider,
        "hindsight_url": hindsight_url,
        "searxng_url": searxng_url,
        "compose_profiles": profiles,
    }
    atomic_write(STATE / "install.json", json.dumps(payload, indent=2) + "\n", private=True)


def self_test() -> None:
    for candidate in [
        "127.0.0.1",
        "192.168.1.20",
        "10.0.0.2",
        "172.16.1.4",
        "100.64.0.1",
        "100.119.62.6/16",
    ]:
        validate_private_bind(candidate)
    for rejected in ["0.0.0.0", "::", "8.8.8.8", "1.1.1.1"]:
        try:
            validate_private_bind(rejected)
        except ValueError:
            pass
        else:
            raise AssertionError(f"self-test failed: unsafe bind accepted: {rejected}")
    print("bootstrap self-test passed")


def main() -> int:
    ap = argparse.ArgumentParser(description="Install/configure Hermes Privacy Stack")
    ap.add_argument("--preset", choices=["strict", "balanced", "developer", "minimal"])
    ap.add_argument("--role", choices=["local", "server", "client"])
    ap.add_argument("--bind-address", help="Exact private IPv4 to bind local services (server role).")
    ap.add_argument(
        "--network-provider",
        choices=["auto", "netbird", "tailscale", "manual"],
        default="auto",
        help="Overlay detection preference for server role. 'tailscale' also covers Headscale-managed clients.",
    )
    ap.add_argument("--hindsight-url", help="Existing Hindsight URL for client role.")
    ap.add_argument("--searxng-url", help="Existing SearXNG URL for client role.")
    ap.add_argument("--non-interactive", action="store_true")
    ap.add_argument("--skip-model-setup", action="store_true")
    ap.add_argument("--enable-activepieces", action="store_true", help="Enable the optional local Activepieces profile.")
    ap.add_argument("--self-test", action="store_true", help="Run pure local validation and exit.")
    args = ap.parse_args()

    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ required")
    if args.self_test:
        self_test()
        return 0

    print("\nHermes Privacy Stack — local first, secrets never in Git\n")
    preset = args.preset or (
        "balanced" if args.non_interactive else choose("Privacy preset", ["strict", "balanced", "developer", "minimal"], 2)
    )
    role = args.role or (
        "local" if args.non_interactive else choose("Machine role", ["local", "server", "client"], 1)
    )

    install_hermes(args.non_interactive)
    snapshot_hermes()
    seed_templates(args.non_interactive)
    bind_address, effective_network_provider = select_bind_address(
        role, args.bind_address, args.non_interactive, args.network_provider
    )

    if role == "client":
        hindsight_url = resolve_client_url(
            args.hindsight_url,
            "--hindsight-url / Hindsight private URL",
            args.non_interactive,
            "http://100.100.20.30:8888",
        )
        searxng_url = resolve_client_url(
            args.searxng_url,
            "--searxng-url / SearXNG private URL",
            args.non_interactive,
            "http://100.100.20.30:8088",
        )
        profiles: list[str] = []
    else:
        runtime_searxng = ensure_runtime_searxng()
        write_stack_env(bind_address, runtime_searxng)
        profiles = start_stack(preset, role, bind_address, args.non_interactive, args.enable_activepieces)
        hindsight_url = f"http://{bind_address}:8888"
        searxng_url = f"http://{bind_address}:8088"

    configure_hindsight(hindsight_url)
    configure_privacy_web(searxng_url)
    save_install_state(
        preset,
        role,
        bind_address,
        hindsight_url,
        searxng_url,
        profiles,
        effective_network_provider,
    )
    if command("hermes"):
        run(["hermes", "config", "check"], check=False)

    print("\nCore bootstrap complete.")
    if command("hermes") and not args.skip_model_setup:
        print("\nNext: choose OpenAI Codex / ChatGPT OAuth in Hermes' official model wizard:\n  hermes model")
        if not args.non_interactive and yesno("Open Hermes model setup now?", True):
            run(["hermes", "model"], check=False)
    print(f"\nRun diagnostics anytime: python {ROOT / 'scripts' / 'doctor.py'}")
    if role == "server":
        print(
            f"Server mode is bound only to {bind_address} ({effective_network_provider}). "
            "Restrict service ports further with your overlay ACL/policy or host firewall."
        )
    print("Review ROADMAP.md before enabling optional high-authority MCPs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
