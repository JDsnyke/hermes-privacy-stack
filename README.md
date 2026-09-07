# Hermes Privacy Stack

A privacy-first, local-by-default distribution around **Hermes Agent** and **OpenAI Codex OAuth**. It gives a fresh Hermes instance long-term memory, private search, document parsing, browser automation, curated MCPs/skills, encrypted backups, and a practical multi-device topology without making paid SaaS services part of the foundation.

> **Privacy rule:** Git contains code, templates and reviewed defaults only. OAuth tokens, API keys, `USER.md`, live memory, sessions, service databases, generated runtime secrets and backups stay out of Git.

## Status

**Pre-1.0 / active hardening.** See [ROADMAP.md](ROADMAP.md). The stack is designed so Hermes remains usable when optional services are unavailable.

> **Repository visibility:** GitHub currently reports this repository as **public**. The committed tree is deliberately public-safe, but the intended personal deployment is private. Change repository visibility in GitHub settings if you want the repo itself private.

## Privacy model

- Local installs bind services to `127.0.0.1`.
- Shared-server installs accept only a specific private/Tailscale IP; wildcard/public binds are rejected.
- Hermes search is explicitly pinned to self-hosted SearXNG with keyless fallback/rescue disabled.
- Hindsight is shared by API, never by syncing live DB files.
- SearXNG secrets and Compose runtime state are generated outside Git.
- OpenViking is **not auto-started** until authenticated runtime provisioning is implemented.
- Cloud storage is treated as encrypted backup transport, not trusted plaintext memory storage.

Read [docs/PRIVACY.md](docs/PRIVACY.md) and [docs/THREAT-MODEL.md](docs/THREAT-MODEL.md).

## Architecture

```text
                         OpenAI Codex OAuth
                                │
                         ┌──────▼──────┐
                         │ Hermes Agent│
                         └───┬────┬────┘
                             │    │
                    memory   │    │ tools/context
                             │    │
                    ┌────────▼┐  ┌▼──────────────────────┐
                    │Hindsight│  │ local/private tools  │
                    └────┬────┘  ├─ SearXNG             │
                         │       ├─ Docling              │
                  local Ollama   ├─ Hermes browser       │
                                 └─ Activepieces (opt.)  │

                       private network only
                  (localhost or Tailscale/WireGuard)

Planned authenticated additions:
OpenViking · Firecrawl · Crawl4AI · ToolHive · Windmill · MarkItDown
```

### Current components

| Layer | Current default | Notes |
|---|---|---|
| Agent | Hermes Agent >= 0.21 | Profiles, skills, MCP, cron, browser, memory plugins |
| Primary reasoning | Codex OAuth | Authentication happens in Hermes' own model wizard |
| Long-term memory | Hindsight | External local/self-hosted server; profile-isolated banks |
| Auxiliary memory LLM | Ollama | Container-only background memory inference |
| Search | SearXNG | Explicit backend; anonymous Hermes fallback/rescue disabled |
| Documents | Docling | Local document parsing service |
| Browser | Hermes local browser | Avoids Browserbase by default |
| App automation | Activepieces | Optional single-machine PGLite/MEMORY mode |
| Knowledge context | OpenViking | **Planned secure installer; not auto-started yet** |
| Crawling | Firecrawl / Crawl4AI | Planned optional profiles |

## One-line install

For the intended **private-repository** workflow, authenticate GitHub CLI once:

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

The installer dynamically asks for privacy preset, machine role and optional integrations. Codex OAuth stays inside Hermes' official model flow; this project never asks you to paste OAuth credentials.

## Recommended first install

Choose **Balanced → Local**. That creates:

```text
Hermes
├── Codex OAuth (configured by Hermes)
├── Hindsight → Ollama
├── SearXNG
├── Docling
└── Hermes local browser
```

Activepieces is opt-in. OpenViking and the heavier crawling/MCP layers remain staged until their security/configuration paths are fully automated.

## Multi-device memory

Run one authoritative Hindsight server on an always-on machine and bind it to a specific Tailscale/private IP:

```bash
./install.sh --role server --bind-address 100.64.10.20
```

Then configure another Hermes instance as a client:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.10.20:8888 \
  --searxng-url http://100.64.10.20:8088
```

The default `bank_id_template: hermes-{profile}` lets the same profile share memory across devices while keeping `coder`, `researcher`, and other profiles isolated. See [docs/MEMORY-SYNC.md](docs/MEMORY-SYNC.md) and [docs/TAILSCALE.md](docs/TAILSCALE.md).

## Backup / restore

Sanitized config backup:

```bash
python scripts/backup.py
```

Logical Hindsight memory backup:

```bash
python scripts/backup.py --bank hermes-default
```

Full Hermes backup (contains credentials; encrypt it):

```bash
python scripts/backup.py --mode full
```

Restore tooling is documented in [docs/BACKUP-RESTORE.md](docs/BACKUP-RESTORE.md). Optional rclone-copy support requires explicit confirmation that the destination is an encrypted `crypt` remote.

## Safe updates

```bash
python scripts/update.py --check
python scripts/update.py
```

The updater refuses dirty checkouts, takes a Hermes quick backup, validates before/after, and rolls the repo back if post-update checks fail. Service images and Hermes itself update only when explicitly requested. See [docs/UPGRADE.md](docs/UPGRADE.md).

## Repository map

```text
.
├── install.sh / install.ps1         # bootstrap entrypoints
├── bootstrap.py                     # cross-platform privacy wizard
├── ROADMAP.md                       # living implementation tracker
├── stack/compose.yml                # local service stack
├── presets/                         # install/security presets
├── profile/                         # Hermes distribution template
├── skills/                          # local reviewed skills
├── catalog/                         # MCP/skill/service catalog
├── scripts/                         # doctor, backup, restore, update helpers
├── docs/                            # operational/security documentation
├── site/                            # zero-tracking interactive Pages site
└── .github/                         # CI, Pages, issue/PR privacy templates
```

## Start here

1. [Quick start](docs/QUICKSTART.md)
2. [Architecture](docs/ARCHITECTURE.md)
3. [Privacy principles](docs/PRIVACY.md) · [Threat model](docs/THREAT-MODEL.md)
4. [Memory sync](docs/MEMORY-SYNC.md) · [Tailscale](docs/TAILSCALE.md)
5. [Backup / restore](docs/BACKUP-RESTORE.md) · [Upgrade](docs/UPGRADE.md) · [Uninstall](docs/UNINSTALL.md)
6. [MCP policy/catalog](docs/MCP.md) · [Skills](docs/SKILLS.md) · [Services](docs/SERVICES.md)
7. [Windows](docs/WINDOWS.md) · [macOS](docs/MACOS.md) · [Linux](docs/LINUX.md)
8. [GitHub Pages](docs/PAGES.md)

## Diagnostics

```bash
python scripts/doctor.py
```

For a sanitized support bundle:

```bash
python scripts/doctor.py --json --redact
```

CI also runs the bootstrap's privacy invariants on Windows, macOS and Linux.

## Upstream projects

- Hermes: https://hermes-agent.nousresearch.com/docs/
- Hindsight: https://hindsight.vectorize.io/
- SearXNG: https://docs.searxng.org/
- Docling: https://docling-project.github.io/docling/
- Activepieces: https://www.activepieces.com/docs/
- OpenViking: https://docs.openviking.ai/
- Firecrawl: https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md

## Security

Read [SECURITY.md](SECURITY.md). Treat every MCP server, skill, browser target and automation connector as executable authority. Prefer fewer tools, fewer scopes, fewer listening ports, and fail-closed behavior.
