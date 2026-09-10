# Services

The service list is intentionally smaller than a typical "AI stack." A service is added only when it provides capability Hermes cannot already supply cleanly.

## Core profile

### Hindsight — memory

- Host port: `8888` API, `9999` UI
- Role: primary long-term agent memory
- In local mode: bound to `127.0.0.1`
- In server mode: bound to one explicit private/overlay IP
- Data: sensitive; never expose publicly or sync its live database files

Hermes clients share it through the API using `bank_id_template: hermes-{profile}`.

### Ollama — auxiliary inference

- Host port: **none**
- Role: background Hindsight inference/extraction
- Network: Compose-private only
- Default model: `qwen3.5:4b` unless `HPS_HINDSIGHT_MODEL` overrides it

The frontier/Codex model remains responsible for primary agent reasoning; Ollama handles cheaper local background memory work.

### SearXNG — private metasearch

- Host port: `8088`
- Role: Hermes web-search backend
- Runtime secret: generated outside Git on first install
- Hermes behavior: `web.search_backend=searxng`, keyless fallback/rescue disabled

The container itself listens on `0.0.0.0:8080` **inside its isolated Docker network**; Docker publishes it only to the host IP selected by the installer.

### Docling — document processing

- Host port: `5001`
- Role: local PDF/Office/document parsing and structured extraction
- Required? No; core profile currently starts it, but it can be removed on constrained systems

## Optional current profiles

### Activepieces — application automation

- Compose profile: `automation`
- Host port: `8090`
- Role: self-hosted Composio/Zapier-style connector/workflow layer
- Default topology: PGLite + in-memory queue for one personal machine
- Sensitivity: high; OAuth connections stored here can authorize external accounts

Enable explicitly with `--enable-activepieces` or the install prompt. Do not treat this lightweight topology as a multi-node production deployment.

### Nango Free Self-Hosted — credential boundary + API proxy

- Compose profile: `nango`
- Host ports: `3003` API/dashboard, `3009` Connect UI
- Database: Postgres on the Compose-private network; no host DB port
- Role: OAuth/API-key connection management, token refresh, encrypted credential storage and authenticated API proxy
- Sensitivity: very high; it stores credentials capable of reaching external accounts
- License: Elastic License 2.0
- Free self-host feature boundary: **Auth + Proxy**, not the full Nango runtime

Enable from guided setup or run:

```bash
python scripts/setup_nango.py
```

The setup helper generates Nango's encryption key, DB password and dashboard password outside Git, enables SSRF protections, disables optional telemetry/log storage, and preserves existing secrets on rerun.

Nango is an alternative to Composio for the **auth/proxy** layer. It does not replace Activepieces' workflow builder. Nango Cloud / Enterprise features such as functions, webhooks and managed MCP are deliberately not assumed by this free self-host profile.

Because the free edition has no managed Nango MCP server, Hermes Privacy Stack includes `scripts/nango_proxy.py` and the reviewed `nango-proxy` skill. Read methods are allowed by default; write methods require an explicit `--allow-write` gate.

See [NANGO.md](NANGO.md).

## Staged / not auto-installed

### OpenViking

Useful for a persistent context/knowledge filesystem and MCP, but **not currently started automatically**. Network deployment needs a genuine root API key and model configuration. The previous unauthenticated shortcut was intentionally removed during hardening.

Planned implementation will:

1. generate/store the root key outside Git,
2. require explicit model/embedding choices,
3. bind locally/private only,
4. register MCP with a narrow tool surface,
5. document backup/sync separately from Hindsight.

### Firecrawl

Not bundled in core Compose because the current self-hosted deployment is a heavier multi-service stack. It will be installed from a pinned upstream release only when broad crawling is requested.

### Crawl4AI

Planned lighter crawling alternative/companion. Useful where an agent needs browser-aware extraction but Firecrawl's full stack is unnecessary.

### MarkItDown MCP

Planned lightweight conversion path for simple Office/PDF/URL-to-Markdown jobs. Docling remains the preferred complex-document parser.

### ToolHive

Planned only when the number/authority of MCP servers justifies a dedicated isolation/policy gateway. Adding it to a small stack would increase complexity without enough benefit.

### Windmill

Planned optional code/workflow execution layer for reusable Python/TypeScript/Go/SQL jobs that are too structured for ordinary Hermes cron/skills.

### Langfuse

Optional future observability. Disabled by default because traces themselves may contain sensitive prompts/tool data.

## Image versions

The development channel currently defaults to upstream mutable images but exposes environment overrides in `stack/stack.env.example`. The supply-chain workflow resolves every audited Compose image—including the optional Nango/Postgres images—to immutable digests for release evidence.

**Stable releases must use reviewed/tested versions or digests before v1.0.** Updating the Git repository does not automatically pull service images unless `scripts/update.py --services` is explicitly used.
