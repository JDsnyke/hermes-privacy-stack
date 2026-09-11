# Hermes Privacy Stack

A privacy-first, local-by-default Hermes Agent distribution built around a **strict-free** rule: bundled services must be self-hostable and fully usable without paid feature unlocks, license keys, or Enterprise-only capabilities.

> **Privacy rule:** Git contains code, templates and reviewed defaults only. OAuth tokens, API keys, `USER.md`, live memory, sessions, service databases, generated runtime secrets and backups stay out of Git.

## Status

**Pre-1.0 / strict-free v2 migration.** See [ROADMAP.md](ROADMAP.md).

> **Repository visibility:** GitHub currently reports this repository as **public**. The committed tree is deliberately public-safe. Change repository visibility manually in GitHub settings if you want the repository itself private.

## Strict-free policy

The default architecture excludes services whose self-hosted edition has paid feature unlocks or depends on a commercial control plane. See [docs/STRICT-FREE.md](docs/STRICT-FREE.md).

Removed from the supported stack under this policy:

- Hindsight
- Ollama
- Nango
- Activepieces
- Windmill
- NetBird
- Firecrawl
- ToolHive
- OpenViking

They may be excellent projects, but they do not match this repository's deliberately stricter product rule.

## Architecture

```text
                         ┌────────────────────┐
                         │    Hermes Agent    │
                         └─────────┬──────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
       ┌────────▼────────┐ ┌──────▼──────┐  ┌───────▼────────┐
       │ mcp-memory-     │ │  SearXNG    │  │    Docling     │
       │ service        │ │ private web │  │ docs / PDFs    │
       │ SQLite + MCP   │ │ search      │  │                │
       └────────────────┘ └─────────────┘  └────────────────┘
                │
                │ optional strict-free services
                ├── llama.cpp       local model endpoint
                ├── Crawl4AI        crawling/extraction
                ├── Node-RED        flows/APIs/credentials
                └── Forgejo         private Git

        private transport: Headscale or WireGuard/wg-easy
        planned edge layer: Caddy + Authelia
        file sync: Syncthing (never live databases)
        backup: restic
```

## Model choice

The installer treats the model separately from the self-hosted service stack.

### Strict-free default — local llama.cpp

```bash
./install.sh \
  --model-provider local \
  --llama-model /path/to/model.gguf
```

The generated llama.cpp server uses a 65,536-token context because Hermes expects at least a 64K model context.

### Optional — ChatGPT / Codex OAuth

```bash
./install.sh --model-provider chatgpt-oauth
```

The repository never asks for or stores your OpenAI OAuth token. Authentication remains inside Hermes' own `hermes model` flow. This option is intentionally **optional** and is not part of the strict-free self-hosted baseline.

You can also skip model configuration and run `hermes model` later.

## Current components

| Purpose | Project | Status |
|---|---|---|
| Agent | Hermes Agent | Core |
| Shared semantic memory | mcp-memory-service | Core |
| Private search | SearXNG | Core |
| Documents / PDFs | Docling Serve | Core |
| Local LLM/VLM server | llama.cpp | Optional profile |
| Crawling / extraction | Crawl4AI | Optional `research` profile |
| Automation / API flows | Node-RED | Optional `automation` profile |
| Private Git | Forgejo | Optional `git` profile |
| Browser automation | Playwright MCP | Planned reviewed MCP profile |
| Private networking | Headscale / WireGuard | External network layer |
| Reverse proxy / TLS | Caddy | Planned deployment helper |
| SSO / MFA | Authelia | Planned deployment helper |
| File / Obsidian sync | Syncthing | Planned helper; non-DB files only |
| Encrypted backup | restic | Migration in progress |
| Containers | Podman Compose preferred | Docker Compose compatibility fallback |

## One-line install

For a private GitHub repository workflow, authenticate GitHub CLI once:

```bash
gh auth login
```

### macOS / Linux

```bash
gh repo clone JDsnyke/hermes-privacy-stack "$HOME/.hermes-privacy-stack" -- --depth 1 && "$HOME/.hermes-privacy-stack/install.sh"
```

### Windows PowerShell

```powershell
gh repo clone JDsnyke/hermes-privacy-stack "$HOME\.hermes-privacy-stack" -- --depth 1; & "$HOME\.hermes-privacy-stack\install.ps1"
```

The interactive install asks for preset, machine role and model path. It does **not** ask for secrets.

## Recommended first install

For the self-hosted baseline, choose **Balanced → Local → local llama.cpp**.

That gives you:

```text
Hermes
├── mcp-memory-service
├── SearXNG
├── Docling
├── Crawl4AI
└── llama.cpp (your selected GGUF)
```

For a lighter machine, choose ChatGPT/Codex OAuth or `skip` for the model and run the core services without local inference.

## Presets

- **strict** — core memory/search/docs only; smallest service surface.
- **balanced** — core + Crawl4AI research.
- **developer** — core + Crawl4AI + Node-RED; optionally Forgejo.
- **minimal** — Hermes only; attach external/private endpoints manually.

## Multi-device memory

Run one authoritative `mcp-memory-service` instance on an always-on trusted machine. Other Hermes clients access its Streamable HTTP MCP endpoint through **Headscale or WireGuard**, not by copying the SQLite database.

Server example:

```bash
./install.sh \
  --role server \
  --bind-address 100.64.10.20 \
  --model-provider skip
```

Client example:

```bash
MCP_MEMORY_API_KEY='read-from-your-secret-manager' \
./install.sh \
  --role client \
  --memory-url http://100.64.10.20:8765 \
  --searxng-url http://100.64.10.20:8088 \
  --model-provider chatgpt-oauth
```

The memory API key is accepted only through the process environment, never as a CLI argument.

See [docs/MEMORY-SYNC.md](docs/MEMORY-SYNC.md), [docs/PRIVATE-NETWORKING.md](docs/PRIVATE-NETWORKING.md), and [docs/HEADSCALE.md](docs/HEADSCALE.md).

## Profiles / personalities

Reviewed starter SOUL bundles:

```text
private-personal   general privacy-first assistant
coder              software engineering / architecture
researcher         evidence-first research
operator           infrastructure / automation
```

Install without cloning credentials or memory:

```bash
python scripts/install_profiles.py private-personal coder researcher
```

Existing profile `SOUL.md` files are preserved unless overwrite is explicitly requested. See [docs/PROFILES.md](docs/PROFILES.md).

## Privacy defaults

- Services bind to `127.0.0.1` for local installs.
- Server role accepts only exact private/CGNAT/LAN addresses; `0.0.0.0`, `::` and global addresses are rejected.
- SearXNG is the explicit Hermes search backend; keyless fallback/rescue is disabled.
- mcp-memory-service requires a generated local API key.
- Node-RED gets a generated credential-encryption secret.
- Secrets are stored in machine-local state outside Git.
- Live SQLite/service databases are never synchronized through Syncthing/Drive/Dropbox.
- High-authority skills and MCPs remain review-first.

## Container runtime

The bootstrap prefers:

```text
Podman Compose
      ↓ fallback
Docker Compose
```

Podman is preferred because it keeps the strict-free baseline independent of Docker Desktop licensing. Existing Docker Engine users can continue using Docker Compose.

## Backup / restore

The v2 target is:

```text
logical/service-safe export
        ↓
local staging bundle
        ↓
restic encrypted snapshots
        ↓
NAS / second machine / removable disk
```

Do not copy a live mcp-memory-service SQLite database between machines. Backup tooling is being migrated from the old Hindsight workflow; see [docs/BACKUP-RESTORE.md](docs/BACKUP-RESTORE.md) and `ROADMAP.md` for current status.

## Diagnostics

```bash
python scripts/doctor.py
```

Sanitized machine-readable output:

```bash
python scripts/doctor.py --json --redact
```

## Repository map

```text
.
├── install.sh / install.ps1
├── bootstrap.py
├── ROADMAP.md
├── stack/compose.yml
├── presets/
├── profile/
├── templates/profiles/
├── skills/
├── catalog/
├── scripts/
├── docs/
├── site/
└── .github/
```

## Start here

1. [Quick start](docs/QUICKSTART.md)
2. [Strict-free policy](docs/STRICT-FREE.md)
3. [Architecture](docs/ARCHITECTURE.md)
4. [Models](docs/MODELS.md)
5. [Privacy](docs/PRIVACY.md) · [Threat model](docs/THREAT-MODEL.md)
6. [Memory sync](docs/MEMORY-SYNC.md)
7. [Private networking](docs/PRIVATE-NETWORKING.md) · [Headscale](docs/HEADSCALE.md)
8. [Services](docs/SERVICES.md) · [MCP](docs/MCP.md) · [Skills](docs/SKILLS.md)
9. [Profiles](docs/PROFILES.md)
10. [Backup / restore](docs/BACKUP-RESTORE.md)

## Upstream projects

- Hermes Agent — https://github.com/NousResearch/hermes-agent
- llama.cpp — https://github.com/ggml-org/llama.cpp
- mcp-memory-service — https://github.com/doobidoo/mcp-memory-service
- SearXNG — https://github.com/searxng/searxng
- Docling — https://github.com/docling-project/docling
- Crawl4AI — https://github.com/unclecode/crawl4ai
- Node-RED — https://github.com/node-red/node-red
- Forgejo — https://codeberg.org/forgejo/forgejo
- Playwright MCP — https://github.com/microsoft/playwright-mcp
- Headscale — https://github.com/juanfont/headscale
- Authelia — https://github.com/authelia/authelia
- Caddy — https://github.com/caddyserver/caddy
- Syncthing — https://github.com/syncthing/syncthing
- restic — https://github.com/restic/restic
- Podman — https://github.com/containers/podman

## Security

Read [SECURITY.md](SECURITY.md). Treat every MCP server, browser target, workflow and skill as executable authority. Prefer fewer tools, smaller scopes, private bindings and fail-closed behavior.
