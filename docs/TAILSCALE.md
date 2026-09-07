# Tailscale / private multi-device networking

The stack does not need a public reverse proxy for personal multi-device memory. Prefer a private tailnet.

## Server

1. Install and sign into Tailscale on the always-on host.
2. Get its IPv4 address:

```bash
tailscale ip -4
```

3. Install the stack in server mode, binding to that exact address:

```bash
./install.sh --role server --bind-address 100.64.10.20
```

The installer rejects `0.0.0.0`, `::` and globally routable addresses.

## Clients

Join each client device to the same tailnet and point it at the server:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.10.20:8888 \
  --searxng-url http://100.64.10.20:8088
```

## ACL principle

A Tailscale IP is private routing, not automatically least privilege. Restrict service ports to only the devices/users that need them.

Typical personal exposure from the core stack:

| Port | Service | Need from clients? |
|---:|---|---|
| 8888 | Hindsight API | Yes |
| 9999 | Hindsight UI | Usually admin device only |
| 8088 | SearXNG | Yes if clients share search |
| 5001 | Docling | Optional |
| 8090 | Activepieces | Optional/admin only |

Prefer denying `9999`, `5001` and `8090` to ordinary clients unless needed.

## Why direct private bind instead of `0.0.0.0`

Binding Docker to the Tailscale/RFC1918 address prevents the service from automatically listening on every host interface. This reduces accidental LAN/Wi-Fi/public-interface exposure even before firewall rules are considered.

## Tailscale Serve

Tailscale Serve can be a good future option for authenticated HTTPS names while services remain loopback-only. The current installer uses direct private-IP binds because they are simple and portable across Windows/macOS/Linux. A Serve-based mode is tracked in ROADMAP.md.

## Do not expose unauthenticated services publicly

Hindsight and SearXNG are intended to stay on localhost/private networks in this stack. OpenViking requires a real root key before network exposure and is therefore not automatically started by the installer yet.
