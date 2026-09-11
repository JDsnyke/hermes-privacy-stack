# Multi-device memory

Hermes Privacy Stack v2 uses one authoritative **mcp-memory-service** instance for shared semantic memory.

## Rule: share the API, never the live database

Do not synchronize the live SQLite-vec database with Syncthing, Google Drive, Dropbox or similar tools.

Multiple clients should access the same authenticated MCP endpoint over Headscale/WireGuard.

```text
Hermes A ──┐
Hermes B ──┼── private network ── mcp-memory-service ── SQLite-vec
Hermes C ──┘
```

## Server

Example:

```bash
./install.sh \
  --role server \
  --bind-address 100.64.10.20 \
  --model-provider skip
```

The generated API key lives in the server's private stack state (`stack.env`) outside Git.

Default endpoint:

```text
http://100.64.10.20:8765/mcp
```

Restrict port 8765 so only approved clients can reach it.

## Client

Transfer the memory API key through a password manager, secret manager or another secure channel. Do not paste it into Git, documentation, shell history or chat.

Expose it only to the installer process:

```bash
MCP_MEMORY_API_KEY='...' \
./install.sh \
  --role client \
  --memory-url http://100.64.10.20:8765 \
  --searxng-url http://100.64.10.20:8088 \
  --model-provider chatgpt-oauth
```

The installer writes the key to the local Hermes `.env` and configures Hermes' memory MCP with an Authorization header. It is never accepted as a command-line argument.

## Memory scope

Unlike the old Hindsight bank template, mcp-memory-service does not automatically create a separate database per Hermes profile in this stack.

Use tags/namespaces deliberately. Recommended conventions:

```text
profile:private-personal
profile:coder
profile:researcher
profile:operator
project:<project-name>
source:<source-type>
```

A future profile policy layer will make these tags automatic. Until then, avoid storing sensitive or project-specific information without enough context to retrieve it safely.

## Local Hermes memory vs shared MCP memory

They serve different purposes:

- `USER.md` / `MEMORY.md` — local Hermes-owned durable context and preferences.
- mcp-memory-service — shared semantic memories accessible to approved clients.

Do not blindly duplicate every local memory into shared memory.

## Writes and deletions

Memory is an external persistent side effect. Recommended policy:

- storing durable preferences/decisions: allowed after normal memory judgment,
- storing sensitive personal data: require clear user value and minimization,
- deleting/consolidating memories: require explicit user intent,
- passwords/tokens/cookies/recovery codes/private keys: never store.

Hermes' own memory-write approval remains enabled in strict/balanced profiles; MCP memory authority should receive a separate tool allowlist.

## Backups

Use service-safe SQLite backup/export procedures and restic snapshots. Never copy a database while multiple writers are modifying it unless the storage project's documented backup method guarantees consistency.

The backup/restore implementation is being migrated and tracked in `ROADMAP.md`.
