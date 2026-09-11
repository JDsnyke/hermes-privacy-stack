# Services

Only strict-free supported runtime services are listed here. A supported service must be self-hostable and fully usable for its assigned role without paid feature unlocks.

## Core

### mcp-memory-service

Purpose: shared semantic memory across Hermes clients.

```text
profile: core
host port: 8765
storage: SQLite-vec in a persistent volume
auth: generated API key
```

Hermes connects through Streamable HTTP MCP. The database is authoritative on one server; clients never synchronize its live files.

### SearXNG

Purpose: private search discovery.

```text
profile: core
host port: 8088
```

Hermes is configured to use SearXNG explicitly and fail closed rather than silently using anonymous external search fallback.

### Docling Serve

Purpose: local PDF/document parsing and conversion.

```text
profile: core
host port: 5001
```

Keep document processing local unless the user explicitly chooses another path.

## Optional local model

### llama.cpp

Purpose: local OpenAI-compatible model server.

```text
profile: local-model
host port: 8080
model: user-selected GGUF
context: 65536
```

No model is downloaded automatically. The selected model directory is mounted read-only.

ChatGPT/Codex OAuth remains a separate optional Hermes model path and does not require this service.

## Research

### Crawl4AI

Purpose: local crawling and clean-content extraction.

```text
profile: research
host port: 11235
```

Recommended routing:

```text
SearXNG -> find candidate URLs
Crawl4AI -> extract ordinary pages
Playwright MCP -> interactive/browser-required sites
Docling -> PDFs/documents
```

Playwright MCP is planned but not yet automatically configured.

## Automation

### Node-RED

Purpose: workflows, webhooks, APIs and external-service integration.

```text
profile: automation
host port: 1880
credential encryption: generated NODE_RED_CREDENTIAL_SECRET
```

Node-RED is a high-authority surface. Restrict editor access to operator/admin devices and do not expose it publicly by default.

The v2 architecture uses Node-RED plus native MCP/API clients instead of Nango, Activepieces, Windmill or Composio-style platform dependencies.

## Git

### Forgejo

Purpose: canonical self-hosted Git/config repository.

```text
profile: git
HTTP: 3000
SSH: 2222
```

The current profile is intentionally simple. Registration hardening, authentication and reverse-proxy integration remain roadmap items.

GitHub can remain an optional mirror/development host; it is not required by the runtime architecture.

## External infrastructure planned around the stack

These are strict-free projects but are not yet auto-provisioned by the Compose file because they need deployment-specific inputs.

### Headscale

Self-hosted private-mesh coordination. Clients use compatible Tailscale client software against your Headscale control plane.

### WireGuard / wg-easy

Simpler private network for static/small deployments.

### Caddy

Reverse proxy/TLS edge. Will be used for explicitly selected browser-facing services.

### Authelia

SSO/MFA/access policy in front of Caddy-managed services.

### Syncthing

Peer-to-peer sync for ordinary documents/Obsidian/config exports only. Never synchronize live databases.

### restic

Encrypted, deduplicated backups to local/NAS/SFTP/object destinations. Becoming the default backup backend.

### Podman

Preferred container runtime. Docker Compose remains supported for compatibility.

## Removed services

The previous architecture contained or planned:

```text
Hindsight
Ollama
Nango
Activepieces
Windmill
NetBird
Firecrawl
ToolHive
OpenViking
```

They are no longer supported profiles under the strict-free rule. See [STRICT-FREE.md](STRICT-FREE.md).
