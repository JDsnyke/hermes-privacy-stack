#!/usr/bin/env python3
"""Detect a safe private overlay address without coupling the stack to one VPN vendor.

Supported auto-detection:
- NetBird: `netbird status --ipv4`
- Tailscale or Headscale-managed Tailscale clients: `tailscale ip -4`

Netmaker and plain WireGuard remain manual because interface names/address allocation are deployment-specific.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import shutil
import subprocess
import sys


def validate_private_ip(value: str) -> str:
    raw = value.strip().split("/", 1)[0]
    if raw in {"", "0.0.0.0", "::", "*"}:
        raise ValueError("empty/wildcard addresses are unsafe")
    ip = ipaddress.ip_address(raw)
    cgnat = ipaddress.ip_network("100.64.0.0/10")
    if not (ip.is_loopback or ip.is_private or ip.is_link_local or (ip.version == 4 and ip in cgnat)):
        raise ValueError(f"{raw} is globally routable")
    if ip.version != 4:
        raise ValueError("this helper currently selects IPv4 only")
    return raw


def run_output(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode:
        return None
    return proc.stdout.strip()


def detect_netbird() -> dict | None:
    value = run_output(["netbird", "status", "--ipv4"])
    if not value:
        return None
    try:
        address = validate_private_ip(value.splitlines()[0])
    except (ValueError, IndexError):
        return None
    return {"provider": "netbird", "address": address, "command": "netbird status --ipv4"}


def detect_tailscale() -> dict | None:
    value = run_output(["tailscale", "ip", "-4"])
    if not value:
        return None
    for line in value.splitlines():
        try:
            address = validate_private_ip(line)
        except ValueError:
            continue
        return {
            "provider": "tailscale-or-headscale",
            "address": address,
            "command": "tailscale ip -4",
        }
    return None


def detect_all() -> list[dict]:
    found = []
    for fn in (detect_netbird, detect_tailscale):
        result = fn()
        if result and all(x["address"] != result["address"] for x in found):
            found.append(result)
    return found


def self_test() -> None:
    for good in ("127.0.0.1", "10.0.0.5", "172.16.4.2", "192.168.50.7", "100.64.10.20", "100.119.62.6/16"):
        validate_private_ip(good)
    for bad in ("", "0.0.0.0", "8.8.8.8", "1.1.1.1"):
        try:
            validate_private_ip(bad)
        except ValueError:
            continue
        raise AssertionError(f"unsafe address accepted: {bad}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect a private overlay address for Hermes Privacy Stack")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--address", help="Validate a manually selected overlay/private IPv4 address")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("private-network self-test passed")
        return 0

    if args.address:
        result = {"provider": "manual", "address": validate_private_ip(args.address)}
        print(json.dumps(result) if args.json else result["address"])
        return 0

    found = detect_all()
    if args.json:
        print(json.dumps({"detected": found}, indent=2))
    elif found:
        for item in found:
            print(f"{item['provider']}: {item['address']}  ({item['command']})")
        print(f"\nSuggested server install:\n  ./install.sh --role server --bind-address {found[0]['address']}")
    else:
        print("No NetBird or Tailscale/Headscale overlay address detected.")
        print("For Netmaker/plain WireGuard, supply the assigned private interface IPv4 manually.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
