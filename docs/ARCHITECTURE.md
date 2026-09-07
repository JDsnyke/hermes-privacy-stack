# Architecture

The stack separates five trust domains:

1. **Reasoning** — Hermes + Codex OAuth.
2. **Durable personal/project memory** — Hindsight.
3. **Knowledge/context** — files, Obsidian and optionally OpenViking.
4. **External tools** — MCP / Activepieces / browser.
5. **Backup transport** — encrypted archives copied to cloud storage.

Keeping these separate prevents a convenience feature such as Drive sync from becoming the storage engine for live memory databases.

## Roles

### Local
All core services run on the same computer and bind to loopback.

### Server
Core services run on an always-on trusted machine. Clients reach them only through a private network. Do not bind service ports to `0.0.0.0` merely to make them reachable.

### Client
Hermes runs locally. Hindsight/Search/knowledge endpoints point to a private server. Model OAuth remains local to that client.

## Why Hindsight + OpenViking are not both primary memory

Hermes supports one external memory provider at a time. Hindsight is the default primary memory because it is designed for learned long-term memory. OpenViking is optional as a context/knowledge service exposed through MCP/API instead of competing for the memory-provider slot.
