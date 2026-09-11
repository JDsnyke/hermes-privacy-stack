# Privacy principles

See [THREAT-MODEL.md](THREAT-MODEL.md) for the detailed threat model and [STRICT-FREE.md](STRICT-FREE.md) for service acceptance policy.

## Protected assets

- OAuth access/refresh tokens
- API keys and connector credentials
- `USER.md`, memories and session history
- files ingested for research/document work
- mcp-memory-service data
- Node-RED credential state
- browser cookies/session state
- Forgejo private repositories
- backup credentials and archives

## Defaults

### Local first

Local services bind to `127.0.0.1`. Server mode accepts only an exact loopback/private/CGNAT/LAN address and rejects wildcard/global bindings.

### Self-hosted functionality first

The supported runtime stack must remain operational without paid feature unlocks or mandatory commercial control planes. External providers are explicit options, not dependencies.

ChatGPT/Codex OAuth is an example: it is allowed as an optional model path because local llama.cpp remains available and the self-hosted services do not depend on OpenAI.

### Fail-closed web search

Hermes is configured with SearXNG and anonymous keyless fallback/rescue disabled. A broken private search backend should fail rather than silently transmitting the query somewhere else.

### Runtime secrets outside Git

The bootstrap generates machine-local values outside the checkout, including:

- SearXNG secret/config,
- mcp-memory-service API key,
- Node-RED credential-encryption secret,
- topology/install metadata.

OAuth tokens remain managed by Hermes/provider tooling and are never requested by this repository.

### Memory separation

`USER.md` / `MEMORY.md` are Hermes-local durable context. mcp-memory-service is shared semantic memory over authenticated MCP.

Do not store passwords, private keys, cookies, recovery codes, OTPs or OAuth tokens in either memory layer.

### No live database sync

Do not synchronize mcp-memory-service SQLite, Node-RED state, Forgejo databases or other live service databases through Syncthing/Drive/Dropbox.

Use documented backup/export procedures and restic snapshots instead.

### Least authority

- no automatic community-skill installation,
- no automatic high-authority MCP installation,
- agent-created memory/skill writes use approval gates where Hermes supports them,
- Node-RED is optional and treated as high authority,
- Forgejo read/write access should be separated,
- Playwright browser state should be isolated,
- memory deletion requires explicit user intent.

### Private transport

Remote service access should travel through self-hosted Headscale or WireGuard/wg-easy. Detection of a `tailscale` client does not prove it uses Headscale; verify its control server.

## Model privacy

### llama.cpp

Prompts and model output remain on infrastructure you control, subject to your host/network security.

### ChatGPT/Codex OAuth

Selecting OAuth is an explicit privacy boundary change. Prompts/model traffic are sent to the chosen external provider under its terms. The rest of the stack can remain self-hosted.

## Browser / crawling privacy

Prefer the least-powerful tool that works:

```text
SearXNG          discovery
Crawl4AI         ordinary extraction
Docling          documents/PDFs
Playwright MCP   interactive browser work
```

A browser session can contain cookies and authenticated account data. Never mount a personal browser profile into agent automation by default.

## Baseline host security

This stack cannot protect a compromised host. Use full-disk encryption, OS updates, screen lock, passkeys/MFA, secure boot where practical, a password manager and least-privilege local accounts.

## Review rule

Every new service/MCP/skill must answer:

1. What data can it read?
2. What can it write/delete/send?
3. Which ports/processes does it expose?
4. Which credentials/scopes does it require?
5. Does data leave the trusted network?
6. What happens when it fails?
7. Can the same job be done with less authority?
8. Is any capability required for our use case paid or Enterprise-only?

If a required capability is paywalled, the dependency does not enter the supported strict-free stack.
