# Architecture

The stack separates six trust domains:

1. **Reasoning** — Hermes + Codex OAuth.
2. **Durable personal/project memory** — Hindsight.
3. **Knowledge/context** — files, Obsidian and optionally OpenViking.
4. **External tools/workflows** — MCP / Activepieces / browser.
5. **Credential boundary** — optionally Nango Free Self-Hosted for OAuth/API credentials and authenticated proxying.
6. **Backup transport** — encrypted archives copied to cloud storage.

Keeping these separate prevents a convenience feature such as Drive sync from becoming the storage engine for live memory databases, and prevents a general-purpose agent from needing direct access to every provider refresh token.

## Roles

### Local
All core services run on the same computer and bind to loopback. Optional Nango binds its API/dashboard and Connect UI to loopback as well; its Postgres service remains Docker-private.

### Server
Core services run on an always-on trusted machine. Clients reach them only through a private network. Do not bind service ports to `0.0.0.0` merely to make them reachable.

If Nango is hosted here, its private administration endpoint can stay on the overlay while a narrowly scoped HTTPS ingress is used only when an OAuth provider requires a public callback URL. That does **not** justify exposing Hindsight, SearXNG or Docling publicly.

### Client
Hermes runs locally. Hindsight/Search/knowledge endpoints point to a private server. Model OAuth remains local to that client. A client can also use a remote Nango proxy endpoint without storing the external provider's refresh token itself.

## Integration split

### Activepieces
Use for visual/no-code workflows, connectors and application automation.

### Nango Free Self-Hosted
Use for Auth + Proxy: OAuth/API-key connections, refresh-token handling, encrypted credential storage and authenticated requests to provider APIs.

The free self-hosted edition does not provide Nango's full functions/webhooks/MCP runtime. Hermes Privacy Stack therefore integrates it through a local least-authority proxy helper rather than assuming paid features.

### Hermes MCP / skills
Use as the agent-facing capability layer. Prefer narrow MCP tool surfaces and reviewed skills that call either direct local services or a credential boundary such as Nango.

## Why Hindsight + OpenViking are not both primary memory

Hermes supports one external memory provider at a time. Hindsight is the default primary memory because it is designed for learned long-term memory. OpenViking is optional as a context/knowledge service exposed through MCP/API instead of competing for the memory-provider slot.
