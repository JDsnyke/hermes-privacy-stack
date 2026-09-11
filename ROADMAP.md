# Roadmap — strict-free v2

This file is the product plan and implementation tracker. The v2 rule is intentionally strict: bundled services must be self-hosted and fully usable without paid feature unlocks, license keys, Enterprise-only capabilities, or a mandatory commercial control plane.

Legend: `[x]` complete · `[-]` partial/in progress · `[ ]` planned.

## Migration status

### Removed by policy

The following are no longer part of the supported architecture:

- [x] Hindsight → replaced by `mcp-memory-service`
- [x] Ollama → replaced by `llama.cpp`
- [x] Nango → removed; Node-RED/native APIs are the integration path
- [x] Activepieces → replaced by Node-RED
- [x] Windmill → not part of strict-free baseline
- [x] NetBird → removed; Headscale/WireGuard are the supported private transports
- [x] Firecrawl → replaced by Crawl4AI
- [x] ToolHive → removed; Hermes native MCP + container isolation is sufficient
- [x] OpenViking → removed from supported baseline

Historical issues #3 and #6 refer to removed components and should be closed as superseded by this architecture.

## P0 — repository / privacy safety

- [ ] Make GitHub repository private if desired; GitHub currently reports it public. The committed tree must remain public-safe regardless.
- [x] Strict `.gitignore` for credentials, OAuth state, memories, sessions, databases, caches and backups.
- [x] `SECURITY.md`, privacy principles and explicit threat model.
- [x] Secret-pattern scanner and forbidden-runtime-file checks.
- [x] SearXNG explicit search backend with keyless fallback/rescue disabled.
- [x] Runtime-generated SearXNG secret outside Git.
- [x] Runtime-generated mcp-memory-service API key outside Git.
- [x] Runtime-generated Node-RED credential encryption secret outside Git.
- [x] Reject wildcard and globally routable server bindings.
- [x] CI policy gate rejects reintroduction of old open-core/commercial service containers.
- [-] Stable-release image/version/digest pinning and provenance. Image-lock tooling exists; release pins remain. See #4.
- [-] SBOM + vulnerability evidence workflow. Machinery exists; baseline/gating remains. See #4.
- [ ] Release signing/provenance for installer tags. See #4.

## P0 — installer reliability

- [x] macOS/Linux shell and Windows PowerShell entrypoints.
- [x] Cross-platform Python bootstrap.
- [x] Local/server/client roles.
- [x] `strict`, `balanced`, `developer`, `minimal` presets.
- [x] Podman Compose preferred with Docker Compose compatibility fallback.
- [x] Model selection is independent from services.
- [x] Local llama.cpp model option.
- [x] Optional ChatGPT/Codex OAuth option via Hermes' own `hermes model` flow.
- [x] OAuth tokens are never accepted/stored by this repository.
- [x] Client memory secret accepted only through process environment, never command arguments.
- [x] Twice-run idempotency test preserving user-owned files and generated secrets.
- [x] Cross-platform bootstrap/privacy tests on Windows/macOS/Linux CI.
- [ ] Native Windows end-to-end smoke test with Podman/Docker runtime. See #2.
- [ ] macOS Intel + Apple Silicon end-to-end tests. See #2.
- [ ] Linux x86_64 + ARM64 end-to-end tests. See #2.
- [ ] WSL2 end-to-end smoke test. See #2.
- [ ] Native Podman Compose end-to-end validation on Linux and macOS.

## v0.2 — strict-free core stack

### Hermes / models

- [x] Hermes Agent as orchestration layer.
- [x] llama.cpp optional local OpenAI-compatible model server.
- [x] llama.cpp generated configuration uses 65,536-token context.
- [x] Optional ChatGPT/Codex OAuth retained as a non-baseline convenience option.
- [ ] Add model compatibility checker that verifies selected GGUF metadata/context before start.
- [ ] Add GPU-aware llama.cpp launch presets: CUDA, Metal and CPU.
- [ ] Add reviewed local-model recommendations by VRAM/RAM tier without automatic downloads.
- [ ] Add optional local embedding model cache/preflight for mcp-memory-service.

### Shared semantic memory

- [x] Replace Hindsight with Apache-2.0 `mcp-memory-service`.
- [x] Streamable HTTP MCP deployment using SQLite-vec storage.
- [x] Generated API-key authentication.
- [x] Shared authoritative-server topology; no live DB synchronization.
- [x] Hermes receives the memory service through its native MCP configuration.
- [ ] Live MCP integration smoke test: initialize → store → search → delete synthetic memory.
- [ ] Tool allowlist for normal profiles: store/search/list/health; deletion restricted to explicit approval/high-authority profile.
- [ ] Profile/tag namespace conventions to avoid cross-project memory pollution.
- [ ] Backup/restore drill for SQLite-vec using service-safe backup procedure.

### Search / research

- [x] SearXNG core service.
- [x] Privacy-oriented generated configuration.
- [x] Hermes search fail-closed.
- [x] Crawl4AI optional `research` profile.
- [ ] Crawl4AI health/integration smoke test.
- [ ] Research routing skill: SearXNG discovery → Crawl4AI extraction → Playwright when interaction is required → Docling for documents.
- [ ] Per-profile crawl/browser authority limits.

### Documents

- [x] Docling Serve core service.
- [x] Existing document-intake skill.
- [ ] Pin/test a stable Docling Serve image/digest.
- [ ] Add Docling MCP as reviewed optional MCP.
- [ ] Keep MarkItDown as optional lightweight converter only if its dependency footprint materially helps.

### Browser

- [ ] Add pinned Microsoft Playwright MCP profile.
- [ ] Default to isolated browser storage; no reuse of personal browser profile.
- [ ] Document persistent-login profile risks and explicit opt-in workflow.
- [ ] Add domain/operation policy examples for researcher vs operator profiles.

## v0.3 — automation, integrations and MCP governance

### Node-RED

- [x] Node-RED replaces Nango/Activepieces/Windmill as the supported visual workflow/API layer.
- [x] Generated `NODE_RED_CREDENTIAL_SECRET` outside Git.
- [x] Optional `automation` Compose profile.
- [ ] Generate hardened Node-RED settings: authentication, editor access policy and Projects configuration.
- [ ] Add Headscale/WireGuard-only access example.
- [ ] Add OAuth/API integration recipes with least scopes for Google/GitHub/etc. without embedding secrets in flows.
- [ ] Add Hermes-facing webhook/MCP bridge patterns with read/write separation.

### MCP governance

- [x] Hermes native MCP remains the gateway rather than ToolHive.
- [x] High-authority skills/MCPs remain review-first.
- [ ] Rewrite MCP catalog to strict-free entries only.
- [ ] Generate Hermes MCP config from selected catalog entries.
- [ ] Add per-server tool include/exclude presets.
- [ ] Separate read-only and write-enabled profiles.
- [ ] Add Playwright MCP.
- [ ] Add Docling MCP.
- [ ] Add optional filesystem/git MCPs only with explicit root/path restrictions.

## v0.4 — profiles and skills

- [x] `private-personal`, `coder`, `researcher`, `operator` SOUL bundles.
- [x] Safe profile installer that never clones credentials/memory.
- [x] Personality builder with diff preview and backup.
- [x] Memory/skill write-approval defaults.
- [x] Native Hermes skill quarantine/audit wrapper.
- [ ] Update bundled memory-hygiene skill for MCP memory namespaces/tags.
- [ ] Add strict-free source/license/review metadata for every bundled/curated skill.
- [ ] Add per-profile MCP/skill authority presets.

## v0.5 — private networking and remote access

- [x] Remove NetBird from strict-free architecture.
- [x] Headscale-compatible client detection helper.
- [x] Plain WireGuard/wg-easy manual-address path.
- [x] Server service bindings require an exact private address.
- [ ] Headscale deployment helper with pinned version and self-hosted control-plane verification.
- [ ] WireGuard/wg-easy deployment helper.
- [ ] Two-node Headscale smoke test.
- [ ] Two-node plain-WireGuard smoke test.
- [ ] Least-privilege firewall/ACL examples for memory/search/docs only.

## v0.6 — edge/auth, self-hosted Git and UI

### Caddy + Authelia

- [ ] Add Caddy reverse-proxy/TLS profile/helper.
- [ ] Add Authelia SSO/MFA profile/helper.
- [ ] Ensure public OAuth callback exposure never publishes internal memory/search/admin services.
- [ ] Generate explicit service-by-service access policy.

### Forgejo

- [x] Forgejo LTS optional `git` profile.
- [ ] Harden initial config and disable public registration by default.
- [ ] Add SSH/HTTP access through private network/reverse proxy.
- [ ] Document GitHub as optional mirror rather than canonical runtime dependency.

### Static site

- [x] Dependency-free, zero-tracking interactive site exists.
- [ ] Update site visualizer/config generator to strict-free v2 service list.
- [ ] Serve locally through Caddy.
- [ ] Keep GitHub Pages only as an optional sanitized mirror, not a core dependency.
- [ ] PWA/offline docs.

## v0.7 — files, backup and recovery

### Syncthing

- [ ] Add optional Syncthing helper for Obsidian/docs/config exports.
- [x] Policy: never synchronize live SQLite/service databases.
- [ ] Folder-ignore templates for databases, auth/session state and caches.

### restic

- [ ] Make restic the default encrypted backup backend.
- [ ] Backup sanitized Hermes config + service-safe exports.
- [ ] Include mcp-memory-service service-safe SQLite backup.
- [ ] Include Node-RED/Forgejo logical or cold-consistent backups when enabled.
- [ ] Support local/NAS/SFTP repositories without requiring a cloud provider.
- [ ] Rotation/forget/prune policy with daily/weekly/monthly examples.
- [ ] Automated isolated restore drill.

## v0.8 — observability / supply chain

- [x] Topology-aware `doctor.py` rewritten for strict-free v2.
- [x] Structured/redactable diagnostics.
- [x] Image-lock source policy prevents unreviewed Compose images from silently entering release scans.
- [-] SBOM and vulnerability evidence. See #4.
- [ ] Dependency update automation with human review.
- [ ] Backup freshness and service-health cron examples.

## v1.0 acceptance criteria

A 1.0 release requires:

- [ ] Native Windows, WSL2, macOS Intel, macOS ARM64, Linux x86_64 and Linux ARM64 install tests. See #2.
- [x] No secrets/personal state required in Git.
- [x] Default local stack exposes no public listening ports; server mode rejects wildcard/global binds.
- [ ] Local llama.cpp clean-install/model smoke test on supported OS families.
- [ ] Optional ChatGPT/Codex OAuth smoke test documented separately; failure must not break strict-free local mode.
- [ ] mcp-memory-service authenticated store/search/delete integration test.
- [ ] Two-client shared-memory test over Headscale and WireGuard paths.
- [ ] restic backup + isolated restore succeeds end-to-end.
- [ ] Every enabled MCP has documented trust level/effective tool surface.
- [ ] Every bundled/curated skill has source/license/review metadata.
- [ ] Stable service images are pinned/tested and release artifacts publish provenance/SBOM/security evidence. See #4.
- [ ] No supported runtime service has a paid feature unlock or mandatory commercial control plane.

## Later experiments

Experiments must still satisfy strict-free policy before entering the supported stack:

- local voice/STT/TTS
- Nix/Home Manager
- Dev Containers
- Unraid Community Applications template
- alternative free/open memory implementations
- local multimodal model presets
