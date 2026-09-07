# Quick start

## 1. Prerequisites

- Git
- Python 3.10+
- Docker Desktop / Docker Engine + Compose v2 for the self-hosted service stack
- GitHub CLI if this repository is private

Hermes itself can be installed by the wizard through the official upstream installer.

## 2. Install

Run the one-line command from the root README. Choose **Balanced** and **Local** for a first computer.

## 3. Configure Codex OAuth

Run:

```bash
hermes model
```

Choose the OpenAI Codex / ChatGPT OAuth provider. Complete authentication in the browser. This project never reads or stores the resulting OAuth token.

## 4. Verify memory/search

```bash
hermes memory status
python scripts/doctor.py
```

The default endpoints are Hindsight `127.0.0.1:8888`, Hindsight UI `127.0.0.1:9999`, SearXNG `127.0.0.1:8088`, and Docling `127.0.0.1:5001`.

## 5. Add optional services only when needed

Activepieces, OpenViking and Firecrawl add capability and attack surface. Review [MCP.md](MCP.md) and [PRIVACY.md](PRIVACY.md) first.
