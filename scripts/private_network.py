#!/usr/bin/env python3
"""Validate/detect addresses for the strict-free private-network layer.

Supported paths:
- Headscale control plane with the open-source Tailscale client (`tailscale ip -4`).
- Plain WireGuard / wg-easy via a manually supplied private interface address.

A detected `tailscale` client does NOT prove it is enrolled against Headscale. The user
must verify the control server is self-hosted before treating it as strict-free.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import shutil
import subprocess


def validate_private_ip(value: str) -> str:
    raw = value.strip().split("/", 1)[0]
    if raw in {"", "0.0.0.0", "::", "*"}:
        raise ValueError("empty/wildcard addresses are unsafe")
    ip = ipaddress.ip_address(raw)
    cgnat = ipaddress.ip_network("100.64.0.0/10")
    if ip.version != 4:
        raise ValueError("this helper currently selects IPv4 only")
    if not (ip.is_loopback or ip.is_private or ip.is_link_local or ip in cgnat):
        raise ValueError(f"{raw} is globally routable")
    return raw


def run_output(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def detect_headscale_client() -> dict | None:
    value = run_output(["tailscale", "ip", "-4"])
    if not value:
        return None
    for line in value.splitlines():
        try:
            address = validate_private_ip(line)
        except ValueError:
            continue
        return {
            "provider": "headscale-compatible-client",
            "address": address,
            "command": "tailscale ip -4",
            "warning": "Verify this client is enrolled to your self-hosted Headscale server, not the managed Tailscale control plane.",
        }
    return None


def self_test() -> None:
    for good in ("127.0.0.1", "10.0.0.5", "172.16.4.2", "192.168.50.7", "100.64.10.20"):
        validate_private_ip(good)
    for bad in ("", "0.0.0.0", "8.8.8.8", "1.1.1.1"):
        try:
            validate_private_ip(bad)
        except ValueError:
            continue
        raise AssertionError(f"unsafe address accepted: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Strict-free private-network helper")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--address", help="Validate a Headscale/WireGuard/private LAN IPv4")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("private-network strict-free self-test passed")
        return 0
    if args.address:
        result = {"provider": "manual-wireguard-or-private", "address": validate_private_ip(args.address)}
        print(json.dumps(result) if args.json else result["address"])
        return 0

    found = detect_headscale_client()
    if args.json:
        print(json.dumps({"detected": [found] if found else []}, indent=2))
    elif found:
        print(f"{found['provider']}: {found['address']} ({found['command']})")
        print("WARNING:", found["warning"])
        print(f"\nServer install after verification:\n  ./install.sh --role server --bind-address {found['address']}")
    else:
        print("No Headscale-compatible client address detected.")
        print("For WireGuard/wg-easy, pass the assigned private interface IPv4 with --address or --bind-address.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
