# Architecture

Hermes Privacy Stack v2 separates the system into small trust domains and deliberately avoids commercial/open-core service dependencies.

## Trust domains

1. **Agent** — Hermes Agent.
2. **Inference** — local llama.cpp by default; optional external ChatGPT/Codex OAuth.
3. **Durable semantic memory** — mcp-memory-service over authenticated MCP.
4. **Research/context** — SearXNG, Crawl4AI, Docling and later Playwright MCP.
5. **Automation** — Node-RED, optional and higher authority.
6. **Git/config** — Forgejo plus local Git; GitHub may be an optional mirror.
7. **Private transport** — Headscale or WireGuard/wg-easy.
8. **Edge authentication** — planned Caddy + Authelia.
9. **Backup/sync** — restic for backups; Syncthing only for ordinary non-database files.

## Local topology

```text
Hermes
  ├── MCP ── mcp-memory-service ── SQLite-vec
  ├── web ── SearXNG
  ├── docs ── Docling
  ├── crawl ── Crawl4AI (optional)
  ├── flows ── Node-RED (optional)
  ├── git ── Forgejo (optional)
  └── model
       ├── llama.cpp (local default)
       └── ChatGPT/Codex OAuth (optional external provider)
```

Local services bind to `127.0.0.1` unless server mode is explicitly given a private address.

## Multi-device topology

```text
               Headscale / WireGuard
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       desktop         laptop        workstation
        Hermes          Hermes          Hermes
          │              │              │
          └──────────────┼──────────────┘
                         │
                 always-on host
                  ├── memory:8765
                  ├── search:8088
                  └── docling:5001
```

Clients can use different model providers while sharing the same private memory/search services.

## Why memory is MCP rather than a Hermes-specific provider

The previous architecture coupled long-term memory to Hindsight. v2 instead uses mcp-memory-service because it is an ordinary authenticated MCP service with SQLite-based storage. This makes memory usable by Hermes without coupling the whole stack to a dedicated commercial/open-core memory platform.

Hermes' built-in `MEMORY.md` / `USER.md` facilities remain available. The shared MCP is for cross-device semantic memory and should be treated as a separate authority.

## Container boundary

Podman Compose is preferred. Docker Compose is supported as a compatibility fallback.

Container networking is private by default. A service that needs remote access is published only on an exact private address selected by the operator. Container-internal `0.0.0.0` listeners are acceptable when the host publication is restricted to loopback/private IPs.

## Optional services are not implicit authority

Enabling a Compose profile does not mean Hermes automatically receives unlimited access to it. MCP/tool configuration remains a separate review step. In particular:

- Node-RED is higher authority because flows can modify external systems.
- Forgejo write access should be separated from read access.
- Playwright MCP should use isolated browser state.
- memory deletion should require explicit user intent.

## Planned edge layer

Caddy + Authelia will provide a self-hosted TLS/SSO boundary for browser-facing services. They are intentionally not auto-started yet because domain names, certificates, trusted networks and identity policy must be supplied explicitly rather than guessed by the installer.
