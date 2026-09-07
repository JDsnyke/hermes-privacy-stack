# Quick start

## Prerequisites

- Git
- Python 3.10+
- Docker Desktop / Docker Engine + Compose v2 for the self-hosted services
- GitHub CLI (`gh`) when the repository is private
- Tailscale is strongly recommended only for a shared `server` role

Hermes itself can be installed by the wizard through the official Nous Research installer.

## First machine: local role

Authenticate GitHub CLI once if the repository is private:

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

Choose **Balanced → Local** for the normal first install. Services bind to `127.0.0.1` only.

The bootstrap:

1. installs/keeps Hermes,
2. snapshots existing Hermes config before changing it,
3. creates local `SOUL.md` / `USER.md` only when appropriate,
4. generates a runtime-only SearXNG secret outside Git,
5. starts Ollama + Hindsight + SearXNG + Docling,
6. points Hermes at Hindsight and SearXNG,
7. disables Hermes keyless web fallback/rescue,
8. opens Hermes' own model picker for Codex OAuth.

## Configure Codex OAuth

If you skipped the model picker during install:

```bash
hermes model
```

Choose **OpenAI Codex / ChatGPT OAuth** and authenticate in the browser. This repository never asks for or stores that OAuth token.

## Verify

```bash
hermes memory status
python scripts/doctor.py
```

For a privacy-safe support bundle:

```bash
python scripts/doctor.py --json --redact
```

## Shared memory server

Run one authoritative stack on a machine that is always available. Do **not** use `0.0.0.0`.

Example with a Tailscale address:

```bash
./install.sh --role server --bind-address 100.64.10.20
```

The installer rejects globally routable/wildcard addresses. Apply Tailscale ACLs so only your own client devices can reach ports `8888`, `8088`, `5001` and any optional services.

See [TAILSCALE.md](TAILSCALE.md) and [MEMORY-SYNC.md](MEMORY-SYNC.md).

## Additional client computer

A client does not start the local Docker stack. Point it at the private server:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.10.20:8888 \
  --searxng-url http://100.64.10.20:8088
```

Both URLs are required in non-interactive client mode so web search fails closed instead of silently using another provider.

## Non-interactive example

```bash
./install.sh --preset balanced --role local --non-interactive --skip-model-setup
```

This is suitable for scripted machines. OAuth still needs to be completed through Hermes separately unless it already exists locally.

## Optional services

Activepieces can be enabled during install or with `--enable-activepieces`. It uses the lightweight single-machine PGLite/in-memory-queue topology and should not be treated as a multi-node production deployment.

OpenViking is **not auto-started yet**. Its Docker deployment requires a real root API key and model configuration; the roadmap tracks an authenticated installer rather than shipping an insecure shortcut.

Firecrawl, Crawl4AI, ToolHive, Windmill and other optional layers remain staged additions. Review [MCP.md](MCP.md), [SERVICES.md](SERVICES.md), and [PRIVACY.md](PRIVACY.md) before enabling high-authority integrations.
