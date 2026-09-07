# Hermes Privacy Stack

A privacy-first, local-by-default distribution around **Hermes Agent** and **OpenAI Codex OAuth**. It gives a fresh Hermes instance long-term memory, private search, document parsing, browser automation, curated MCPs/skills, encrypted backups, and a practical multi-device topology without making paid SaaS services part of the foundation.

> **Privacy rule:** Git contains code, templates and reviewed defaults only. OAuth tokens, API keys, `USER.md`, live memory, sessions, service databases and backups stay out of Git.

## Status

**Pre-1.0 / active build.** See [ROADMAP.md](ROADMAP.md). The repository is intentionally designed so an incomplete optional service does not prevent Hermes itself from working.

> Repository visibility check: this project is intended to be private. If it is temporarily public, the committed tree is still designed to be public-safe and contains no personal runtime data.

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
                    │Hindsight│  │ MCP / local services │
                    └────┬────┘  ├─ SearXNG             │
                         │       ├─ Docling              │
                  local Ollama   ├─ Activepieces (opt.)  │
                                 ├─ OpenViking (opt.)    │
                                 └─ Firecrawl (opt.)     │

                       private network only
                  (localhost or Tailscale/WireGuard)
```

### Default components

| Layer | Default | Why |
|---|---|---|
| Agent | Hermes Agent | Native profiles, skills, MCP, cron, browser, memory plugins |
| Primary reasoning | Codex OAuth | Uses ChatGPT/Codex authentication instead of a metered API key |
| Long-term memory | Hindsight | Self-hosted graph/temporal memory with recall + reflect |
| Auxiliary memory LLM | Ollama | Keeps background extraction local |
| Search | SearXNG | Self-hosted metasearch; no search API subscription |
| Documents | Docling | Local PDF/Office/document extraction |
| Browser | Hermes local browser | Avoid Browserbase by default |
| App automation | Activepieces | Optional self-hosted Composio/Zapier-style integration layer |
| Knowledge context | OpenViking | Optional persistent context filesystem/MCP |
| Crawling | Firecrawl | Optional self-hosted crawler; heavier than simple browsing |

## One-line install

### macOS / Linux

For a **private** repository, authenticate GitHub CLI once (`gh auth login`) and run:

```bash
gh repo clone JDsnyke/hermes-privacy-stack "$HOME/.hermes-privacy-stack" -- --depth 1 && "$HOME/.hermes-privacy-stack/install.sh"
```

If the repository is public, this also works:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JDsnyke/hermes-privacy-stack/main/install.sh)
```

### Windows PowerShell

Private-repo path:

```powershell
gh repo clone JDsnyke/hermes-privacy-stack "$HOME\.hermes-privacy-stack" -- --depth 1; & "$HOME\.hermes-privacy-stack\install.ps1"
```

Public-repo path:

```powershell
irm https://raw.githubusercontent.com/JDsnyke/hermes-privacy-stack/main/install.ps1 | iex
```

The installer is interactive by default and asks for machine role, privacy preset, memory topology and optional services. It deliberately sends model/OAuth setup through Hermes' own setup flow rather than asking you to paste OAuth tokens into this project.

## Presets

- **Strict** — localhost/private-tailnet only, smallest tool surface, no telemetry, optional services off by default.
- **Balanced** — recommended personal setup; Hindsight + SearXNG + Docling, local browser, optional Activepieces.
- **Developer** — Balanced + Codex runtime/developer tools and reviewed coding skills.
- **Minimal** — Hermes first, then memory/search only; suitable for laptops and testing.

## Multi-device memory

Do **not** sync live Hindsight/Postgres/SQLite files using Drive/Dropbox/Syncthing. Run one authoritative Hindsight server and point every Hermes instance at it over a private tailnet. Use `bank_id_template: hermes-{profile}` so the same profile shares memory across devices without mixing unrelated profiles.

Encrypted cloud storage is for **backups and portable config**, not live database files. See [docs/MEMORY-SYNC.md](docs/MEMORY-SYNC.md).

## Repository map

```text
.
├── install.sh / install.ps1         # bootstrap entrypoints
├── bootstrap.py                     # cross-platform wizard
├── ROADMAP.md                       # implementation tracker
├── stack/compose.yml                # local service stack
├── presets/                         # install/security presets
├── profile/                         # Hermes distribution template
├── skills/                          # local reviewed skills
├── catalog/                         # MCP/skill/service catalog
├── scripts/                         # doctor, backup, update, config helpers
├── docs/                            # operational documentation
├── site/                            # zero-tracking interactive Pages site
└── .github/workflows/ci.yml         # validation + secret hygiene
```

## Start here

1. [Quick start](docs/QUICKSTART.md)
2. [Architecture](docs/ARCHITECTURE.md)
3. [Privacy & threat model](docs/PRIVACY.md)
4. [Memory sync](docs/MEMORY-SYNC.md)
5. [MCP policy/catalog](docs/MCP.md)
6. [Skills](docs/SKILLS.md)
7. [Backup and restore](docs/BACKUP-RESTORE.md)
8. [Windows](docs/WINDOWS.md) · [macOS](docs/MACOS.md) · [Linux](docs/LINUX.md)

## Upstream documentation

- Hermes: https://hermes-agent.nousresearch.com/docs/
- Hindsight: https://hindsight.vectorize.io/
- OpenViking: https://docs.openviking.ai/
- Activepieces: https://www.activepieces.com/docs/
- Firecrawl self-hosting: https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md
- Docling: https://docling-project.github.io/docling/

## Security

Read [SECURITY.md](SECURITY.md). Treat every MCP server, skill, browser target and automation connector as code with authority. Install fewer tools, expose fewer ports, and grant the narrowest permissions possible.
