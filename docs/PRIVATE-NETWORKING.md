# Private networking

The strict-free stack supports two private-network families:

1. **Headscale** — self-hosted coordination with compatible Tailscale clients.
2. **WireGuard** — directly managed, optionally with wg-easy for administration.

NetBird and the managed Tailscale control plane are intentionally not part of the supported strict-free baseline.

## What the network protects

A shared server may expose these ports only on its private interface:

```text
8765   mcp-memory-service
8088   SearXNG
5001   Docling
11235  Crawl4AI (optional)
1880   Node-RED (admin/high authority; restrict further)
3000   Forgejo HTTP (optional)
2222   Forgejo SSH (optional)
8080   llama.cpp (only if remote inference is intentionally shared)
```

Most clients should need only memory/search/docs.

## Never use wildcard host publication

Do not solve reachability problems by binding the Compose stack to `0.0.0.0` or `::`.

Use:

```bash
./install.sh --role server --bind-address <private-ip>
```

The bootstrap rejects public/global addresses.

## Headscale

Headscale gives moving laptops/desktops a stable private mesh while keeping the coordination server under your control.

The helper can detect the IPv4 advertised by a compatible Tailscale client:

```bash
python scripts/private_network.py
```

Detection alone cannot prove which control server enrolled that client. Verify it is pointed at your Headscale instance before treating the connection as strict-free.

See [HEADSCALE.md](HEADSCALE.md).

## WireGuard / wg-easy

For a small stable set of devices, plain WireGuard has fewer moving parts.

After assigning a private address to the server interface:

```bash
python scripts/private_network.py --address 10.50.0.2
./install.sh --role server --bind-address 10.50.0.2
```

wg-easy can simplify peer administration, but the network should still be designed as ordinary WireGuard rather than making application services publicly reachable.

## Least-privilege firewall model

Example policy:

```text
ordinary Hermes clients
  allow -> server:8765 memory
  allow -> server:8088 search
  allow -> server:5001 docs

researcher clients
  + allow -> server:11235 Crawl4AI

admin/operator devices
  + allow -> server:1880 Node-RED
  + allow -> server:3000 Forgejo UI
  + allow -> server:2222 Forgejo SSH
```

Do not expose an administrative UI simply because another service on the same machine needs remote access.

## Public OAuth callbacks later

Some external OAuth providers require a public HTTPS callback. The future Caddy/Authelia edge design must expose only the exact callback/service route required. A public callback must never implicitly publish memory, SearXNG, Docling or Node-RED.

## DNS

Private DNS is optional. IP-based service URLs are simpler during early setup. If private DNS is used, make sure DNS resolution itself stays within the trusted network and certificates/hostnames are managed consistently.
