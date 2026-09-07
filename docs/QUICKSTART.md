# Quick start

## Prerequisites

- Git
- Python 3.10+
- Docker Desktop / Docker Engine + Compose v2 for the self-hosted services
- GitHub CLI (`gh`) when the repository is private
- For shared-server mode, a trusted private overlay such as **NetBird, Headscale/Tailscale, Netmaker or WireGuard**

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

### Stage 1 — core bootstrap

The bootstrap:

1. installs/keeps Hermes,
2. snapshots existing Hermes config before changing it,
3. creates local `SOUL.md` / `USER.md` only when appropriate,
4. generates a runtime-only SearXNG secret outside Git,
5. starts Ollama + Hindsight + SearXNG + Docling,
6. points Hermes at Hindsight and SearXNG,
7. disables Hermes keyless web fallback/rescue,
8. opens Hermes' own model picker for Codex OAuth.

### Stage 2 — guided privacy/profile setup

Interactive installs then run a second-stage wizard. It can:

- create isolated `private-personal`, `coder`, and `researcher` profiles,
- optionally create the high-authority `operator` profile,
- create profiles in **lean** mode without the full bundled-skill seed,
- launch the personality/SOUL builder with diff preview,
- enable approval before Hermes persists memory and agent-created skill writes,
- enable scanning of agent-created skill content,
- validate the final Hermes configuration.

No credentials or personal profile facts are requested by this second stage.

It is state-aware and does not repeat on every install. Revisit it explicitly with:

```bash
python scripts/guided_setup.py --force
```

Set `HPS_SKIP_GUIDED=1` if you deliberately want only the core bootstrap. `--non-interactive` and `--self-test` skip the guided stage automatically.

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

When Hindsight is running, test the real memory path with a temporary synthetic bank:

```bash
python scripts/hindsight_smoke.py
```

The script performs synchronous **retain → recall → reflect**, checks synthetic markers, and deletes the test bank afterward.

## Profiles and personalities

List bundled roles:

```bash
python scripts/install_profiles.py --list
```

Create least-authority/lean profiles explicitly:

```bash
python scripts/install_profiles.py private-personal coder researcher --lean
```

Preview a custom SOUL without writing:

```bash
python scripts/build_personality.py --profile coder
```

See [PROFILES.md](PROFILES.md).

## Skills

Prefer Hermes' native Skills Hub security pipeline rather than manually copying community skills into the profile.

Inspect first:

```bash
python scripts/review_skill.py skills-sh/obra/superpowers/verification-before-completion
```

Install only after review:

```bash
python scripts/review_skill.py \
  skills-sh/obra/superpowers/verification-before-completion \
  --profile coder \
  --install
```

The wrapper uses Hermes' native inspect/quarantine/security-scan/audit flow and deliberately does **not** expose `--force`. See [SKILLS.md](SKILLS.md).

## Shared memory server

Run one authoritative stack on a machine that is always available. Do **not** use `0.0.0.0`.

Detect a supported overlay address:

```bash
python scripts/private_network.py
```

### NetBird

```bash
./install.sh --role server --network-provider netbird
```

### Tailscale or a Tailscale client enrolled against Headscale

```bash
./install.sh --role server --network-provider tailscale
```

### Any trusted overlay / deterministic automation

```bash
./install.sh \
  --role server \
  --network-provider manual \
  --bind-address 100.100.20.30
```

The installer rejects globally routable/wildcard addresses. Apply overlay policies/firewall rules so ordinary Hermes clients normally reach only `8888` (Hindsight API) and `8088` (SearXNG); keep admin surfaces restricted separately.

See [PRIVATE-NETWORKING.md](PRIVATE-NETWORKING.md), [NETBIRD.md](NETBIRD.md), [HEADSCALE.md](HEADSCALE.md), [TAILSCALE.md](TAILSCALE.md), and [MEMORY-SYNC.md](MEMORY-SYNC.md).

## Additional client computer

A client does not start the local Docker stack. Point it at the private server:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.100.20.30:8888 \
  --searxng-url http://100.100.20.30:8088
```

Both URLs are required in non-interactive client mode so web search fails closed instead of silently using another provider.

## Non-interactive example

```bash
./install.sh --preset balanced --role local --non-interactive --skip-model-setup
```

This is suitable for scripted machines. The guided profile/personality stage is skipped. OAuth still needs to be completed through Hermes separately unless it already exists locally.

## Optional services

Activepieces can be enabled during install or with `--enable-activepieces`. It uses the lightweight single-machine PGLite/in-memory-queue topology and should not be treated as a multi-node production deployment.

OpenViking is **not auto-started yet**. Its Docker deployment requires a real root API key and model configuration; the roadmap tracks an authenticated installer rather than shipping an insecure shortcut.

Firecrawl, Crawl4AI, ToolHive, Windmill and other optional layers remain staged additions. Review [MCP.md](MCP.md), [SERVICES.md](SERVICES.md), and [PRIVACY.md](PRIVACY.md) before enabling high-authority integrations.
