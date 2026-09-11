# MCP governance

Hermes Privacy Stack v2 uses Hermes' native MCP client rather than a separate commercial/open-core gateway.

## Principles

- Every MCP is executable authority.
- Default to the smallest tool set that solves the task.
- Separate read and write authority.
- Keep credentials outside Git and out of command arguments.
- Prefer local/self-hosted MCP servers that satisfy [STRICT-FREE.md](STRICT-FREE.md).
- Review transport, filesystem roots, network reachability and tool include/exclude lists before enabling a server.

## Implemented: mcp-memory-service

Bootstrap configures the authenticated Streamable HTTP endpoint:

```text
http://<private-host>:8765/mcp
```

The generated API key is stored in the local Hermes `.env`, and Hermes references it from the Authorization header.

Memory tools include store/search/list/delete/health-style capabilities. Normal profiles should not receive unrestricted delete/consolidation authority; a formal allowlist is tracked in the roadmap.

## Planned: Playwright MCP

Use for interactive browser tasks only when SearXNG + Crawl4AI are insufficient.

Security requirements before automatic enablement:

- pin a reviewed package version,
- isolated browser profile/storage,
- no personal browser profile mount by default,
- separate authenticated-session profile when needed,
- document write/download/upload authority,
- constrain browser exposure to the task.

## Planned: Docling MCP

Docling Serve is already part of the core stack. Docling MCP will be an optional direct MCP route once its invocation/version is pinned and validated.

## Filesystem / Git MCPs

These are not enabled by default.

If filesystem access is added, scope it to the narrowest directory possible.

If Git/Forgejo write authority is added, separate:

```text
read profile     status/log/diff/search
write profile    commit/branch/push/merge-related operations
```

A research assistant should not inherit repository-write authority merely because the operator profile needs it.

## No ToolHive dependency

ToolHive is intentionally absent under the strict-free product rule. The stack relies on:

```text
Hermes native MCP configuration
+ tool include/exclude policy
+ Podman/container process isolation where useful
+ private network/firewall policy
```

That keeps the authority graph smaller and easier to audit.

## Catalog

`catalog/mcps.json` is the machine-readable review list. Adding a catalog entry does not automatically install or enable it.
