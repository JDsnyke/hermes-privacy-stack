# Tailscale / Headscale notes

> The stack is now provider-agnostic. Start with [PRIVATE-NETWORKING.md](PRIVATE-NETWORKING.md) for the current comparison of **NetBird, Headscale, Tailscale, Netmaker and plain WireGuard**.

Tailscale remains an excellent convenience option, and Headscale provides a self-hosted Tailscale-compatible control plane for personal/small deployments.

## Server

With Tailscale or a Headscale-managed Tailscale client, obtain the overlay IPv4 address:

```bash
tailscale ip -4
```

Then bind Hermes Privacy Stack to that exact address:

```bash
./install.sh --role server --bind-address 100.64.10.20
```

The installer rejects `0.0.0.0`, `::` and globally routable addresses.

## Clients

Join each client to the same overlay and point it at the server:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.10.20:8888 \
  --searxng-url http://100.64.10.20:8088
```

## ACL/policy principle

A private overlay IP is private routing, not automatically least privilege. Restrict service ports to only the devices/users that need them.

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

Binding Docker to the exact overlay address prevents services from automatically listening on every host interface. This reduces accidental LAN/Wi-Fi/public-interface exposure even before network policy is considered.

## Tailscale vs Headscale

- **Tailscale:** easiest operational path; managed coordination/control plane.
- **Headscale:** self-hosted open-source implementation of the Tailscale control server, intentionally scoped primarily to a single personal/small-organization tailnet.

Both use the Tailscale client command above, so Hermes Privacy Stack does not need to care which control plane is behind it.

## Do not expose unauthenticated services publicly

Hindsight and SearXNG are intended to stay on localhost/private overlays. OpenViking requires a real root key before network exposure and is therefore not automatically started by the installer yet.
