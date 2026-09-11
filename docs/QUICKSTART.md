# Quick start

Hermes Privacy Stack v2 is a strict-free, self-hosted baseline around Hermes Agent.

## 1. Requirements

- Python 3.10+
- Git
- Podman + Podman Compose preferred, or Docker Engine + Docker Compose as a compatibility fallback
- Hermes Agent (the bootstrap can install it)
- for local inference: an existing GGUF model with at least 64K supported context

## 2. Clone and run

macOS/Linux:

```bash
gh repo clone JDsnyke/hermes-privacy-stack "$HOME/.hermes-privacy-stack" -- --depth 1
"$HOME/.hermes-privacy-stack/install.sh"
```

Windows PowerShell:

```powershell
gh repo clone JDsnyke/hermes-privacy-stack "$HOME\.hermes-privacy-stack" -- --depth 1
& "$HOME\.hermes-privacy-stack\install.ps1"
```

## 3. Choose a model

### Local llama.cpp

Interactive setup lists local inference first. To make the choice explicit:

```bash
./install.sh \
  --model-provider local \
  --llama-model /path/to/model.gguf
```

The model file is not copied into the repository. Its directory is mounted read-only into llama.cpp.

### Optional ChatGPT / Codex OAuth

```bash
./install.sh --model-provider chatgpt-oauth
```

Hermes' own model wizard handles browser/OAuth authentication. This repository never asks for the OAuth token.

### Configure later

```bash
./install.sh --model-provider skip
hermes model
```

See [MODELS.md](MODELS.md).

## 4. Presets

### Strict

```text
Hermes
mcp-memory-service
SearXNG
Docling
```

### Balanced

Adds Crawl4AI for local research extraction.

### Developer

Adds Crawl4AI + Node-RED and can optionally start Forgejo.

### Minimal

Runs Hermes without the local Compose service set. Use this for a client-only or hand-managed deployment.

## 5. Local vs server vs client

### Local

Everything binds to `127.0.0.1`.

### Server

Use an exact Headscale/WireGuard/LAN address:

```bash
./install.sh \
  --role server \
  --bind-address 100.64.10.20 \
  --model-provider skip
```

Wildcard/public addresses are rejected.

### Client

The memory secret is supplied only in the process environment:

```bash
MCP_MEMORY_API_KEY='...' \
./install.sh \
  --role client \
  --memory-url http://100.64.10.20:8765 \
  --searxng-url http://100.64.10.20:8088 \
  --model-provider chatgpt-oauth
```

Do not place the key in shell scripts, Git or command arguments.

## 6. What the bootstrap writes

Machine-local state is stored outside the checkout.

It includes:

- generated SearXNG secret/config,
- mcp-memory-service API key,
- Node-RED credential secret,
- selected service/model topology,
- optional llama.cpp model path metadata.

Hermes' local `.env` receives only the runtime values it needs.

The repository itself remains reusable and secret-free.

## 7. Diagnostics

```bash
python scripts/doctor.py
```

or:

```bash
python scripts/doctor.py --json --redact
```

## 8. Profiles

After the bootstrap, guided setup can create:

```text
private-personal
coder
researcher
operator
```

Manual example:

```bash
python scripts/install_profiles.py private-personal coder researcher
```

## 9. Next security steps

For a multi-device deployment:

1. deploy Headscale or WireGuard,
2. bind services only to the private interface,
3. allow ordinary clients only to the ports they need,
4. keep Node-RED/Forgejo admin surfaces restricted,
5. configure encrypted restic backups before treating the server as authoritative storage.

See [STRICT-FREE.md](STRICT-FREE.md), [PRIVATE-NETWORKING.md](PRIVATE-NETWORKING.md), and [PRIVACY.md](PRIVACY.md).
