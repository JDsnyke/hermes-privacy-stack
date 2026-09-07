# Roadmap

This file is both the product plan and implementation tracker. Keep it current as features land. Items marked **P0** block a privacy-first 1.0 release.

Legend: `[x]` complete · `[-]` partial/in progress · `[ ]` planned.

## Current focus: v0.2 hardening

### P0 — privacy and repository safety

- [ ] **Make GitHub repository private** (GitHub currently reports it as public). The committed tree remains public-safe until this is changed.
- [x] Add strict `.gitignore` for credentials, OAuth state, memories, sessions, databases, caches and backups.
- [x] Add `SECURITY.md`, privacy principles and an explicit threat model.
- [x] Add issue/PR templates that warn against submitting secrets and require privacy/rollback review.
- [x] Add CI secret-pattern scanner and forbidden-runtime-file checks.
- [x] Keep GitHub Pages static, dependency-free, remote-asset-free and analytics-free.
- [x] Pin Hermes web search explicitly to SearXNG and disable keyless fallback/rescue.
- [x] Generate SearXNG's secret at runtime outside Git.
- [x] Reject wildcard/globally-routable server binds; permit only loopback/private/Tailscale IPs.
- [x] Remove unauthenticated OpenViking auto-start path until root-key provisioning exists.
- [ ] Add release signing/provenance (GitHub attestations or Sigstore) for installer tags.
- [ ] Pin container images by tested version/digest for stable releases; keep `latest` only on edge/dev channel.
- [ ] Add SBOM generation and container vulnerability scanning.

### P0 — installer reliability

- [x] Cross-platform shell/PowerShell entrypoints.
- [x] Python bootstrap wizard with strict/balanced/developer/minimal presets and local/server/client roles.
- [x] Use official Hermes installer rather than vendoring Hermes.
- [x] Keep Codex OAuth configuration inside Hermes' own model setup.
- [x] Detect Docker/Git/Python/Hermes and provide actionable failures.
- [x] Generate runtime Compose/SearXNG config outside the Git checkout.
- [x] Require explicit Hindsight + SearXNG URLs for non-interactive client installs.
- [x] Snapshot existing Hermes config with native `hermes backup --quick` before bootstrap changes.
- [x] Add bootstrap privacy-invariant self-test to Windows/macOS/Linux CI.
- [ ] Full native-Windows end-to-end smoke test with Docker Desktop and Codex OAuth.
- [ ] macOS Intel + Apple Silicon end-to-end smoke tests.
- [ ] Linux x86_64 + ARM64 end-to-end smoke tests.
- [ ] WSL2 end-to-end smoke test.
- [ ] Idempotent install/upgrade test: run installer twice without overwriting user-owned `SOUL.md`, `USER.md`, credentials or memory.
- [ ] Add automated local/server/client integration test harness with disposable Hindsight banks.

## v0.2 — core local stack

### Memory

- [x] Hindsight as recommended external memory provider.
- [x] External-server topology for multi-device memory.
- [x] `hermes-{profile}` bank template guidance/configuration.
- [x] Local Ollama service reserved for auxiliary Hindsight inference.
- [x] Correct Hindsight Ollama base URL to the upstream-compatible `/v1` endpoint.
- [x] Logical whole-bank export/import helpers; no live database copies.
- [ ] Verify Hindsight retain/recall/reflect and the selected Ollama model on every release.
- [ ] Add bank health/stats/known-recall validation script.
- [ ] Add optional Hindsight `openai-codex` auxiliary provider path for users who prefer no local model.
- [ ] Add bank mission/disposition/retention presets for private-personal, coding and research profiles.

### Search / research

- [x] SearXNG default search service.
- [x] Privacy-oriented SearXNG configuration template with per-install runtime secret.
- [x] Configure `SEARXNG_URL` and Hermes `web.search_backend` during install.
- [x] Disable Hermes keyless search fallback/rescue so private search fails closed.
- [ ] Add optional self-hosted Firecrawl installer using a pinned upstream release.
- [ ] Add Crawl4AI alternative profile and comparison.
- [ ] Upgrade research skill to route browser vs Firecrawl/Crawl4AI vs Docling based on task.

### Documents

- [x] Docling local service and document-intake skill.
- [ ] Pin/test Docling Serve/MCP invocation against a tested upstream release.
- [ ] Add MarkItDown MCP as lightweight converter option.
- [ ] Add optional Paperless-ngx intake integration.

### Browser

- [x] Prefer Hermes local browser rather than Browserbase.
- [ ] Add Lightpanda optional acceleration profile.
- [ ] Add Camofox optional compatibility/anti-detection profile with strong warning.
- [ ] Add browser session/storage isolation guidance per Hermes profile.

## v0.3 — integrations and MCP governance

- [x] MCP catalog with risk classes and default-disabled high-authority servers.
- [x] Activepieces as optional Composio/Zapier-style integration layer.
- [-] Activepieces automated local install exists in lightweight PGLite/MEMORY mode; still needs OAuth callback/Tailscale guidance and a scalable optional topology.
- [ ] Generate Hermes MCP config from selected catalog entries.
- [ ] Add per-tool allowlist generator.
- [ ] Add ToolHive optional isolation/gateway layer when MCP count/authority justifies it.
- [ ] Add Windmill optional code-workflow layer.
- [ ] Add Google Workspace setup guide (Gmail/Calendar/Drive) through Activepieces with minimal OAuth scopes.
- [ ] Add GitHub MCP read-only and write profiles separately.
- [ ] Add authenticated OpenViking installer/MCP with root key stored outside Git.

## v0.4 — skills and personalities

- [x] Built-in privacy-audit, memory-hygiene, document-intake, research-pipeline, multi-instance-sync and backup-restore skills.
- [x] Curated third-party skill catalog design (review before install).
- [ ] Add source hashing + review/license metadata for third-party skill pins.
- [ ] Add skill installer that stages source for diff/review before enabling.
- [ ] Add reviewed popular coding/research skills; never auto-install by popularity alone.
- [x] Starter privacy-first `SOUL.md` and local-only `USER.md` creation.
- [ ] Interactive personality builder with preview/diff before writing.
- [ ] Add `private-personal`, `coder`, `researcher`, and `operator` SOUL/profile bundles.
- [ ] Per-profile Hindsight mission/retention policies.

## v0.5 — multi-device and backup

- [x] Authoritative Hindsight server + private-tailnet design.
- [x] Explicit prohibition on syncing live DB files.
- [x] Server binds directly to a selected private/Tailscale IP rather than `0.0.0.0`.
- [x] Tailscale networking/ACL guide and service-port matrix.
- [x] Hindsight logical bank export/import backup scripts using `hindsight-admin export-bank` / `import-bank`.
- [x] Sanitized configuration backup separate from secret-bearing full Hermes backups.
- [-] rclone crypt copy backend supported for preconfigured encrypted remotes; still needs guided remote setup/verification UX.
- [ ] Restic encrypted repository backend.
- [ ] Optional Syncthing for *non-database* Obsidian/knowledge files.
- [ ] Rotation policy: daily/weekly/monthly snapshots with retention limits.
- [ ] Disaster-recovery drill script that imports into a temporary bank and tests known recall.
- [ ] Optional Tailscale Serve/HTTPS mode with services remaining loopback-only.
- [ ] Optional OpenViking central server + per-client MCP routing over tailnet after authentication support lands.

## v0.6 — interactive UX

- [x] Static interactive site with no third-party JS/CSS/fonts.
- [x] Animated architecture visualization.
- [x] Preset/config command generator.
- [x] Pages workflow is explicit opt-in and no longer fails every push when Pages is disabled.
- [ ] Enable GitHub Pages for this repository (manual workflow or repository setting/variable `HPS_ENABLE_PAGES=true`).
- [ ] PWA/offline documentation.
- [ ] Service dependency graph with live local health import (explicit opt-in; browser-local only).
- [ ] Export generated config as a local JSON download without transmitting it.
- [ ] Interactive threat-model wizard.
- [ ] Dark/light theme persisted locally.

## v0.7 — observability and maintenance

- [x] Topology-aware `doctor.py` with optional-service awareness.
- [x] Structured/redactable diagnostics (`--json --redact`) for support bundles.
- [x] One-command stack update with dirty-tree refusal, native Hermes pre-backup, pre/post validation and repository rollback.
- [x] Hermes and Docker service updates remain separate explicit actions.
- [x] Add install/uninstall/upgrade/backup/restore/threat-model runbooks.
- [ ] Optional self-hosted Langfuse profile, disabled by default.
- [ ] Dependency update bot with human review and release notes.
- [ ] Container vulnerability scanning in CI.
- [ ] Backup freshness and memory-server health cron examples.

## v1.0 acceptance criteria

A release can be tagged 1.0 only when:

- [ ] Installer passes native Windows, WSL2, macOS Intel, macOS ARM64, Linux x86_64 and Linux ARM64 end-to-end tests.
- [x] No secrets or personal state are required in Git.
- [x] Default local stack exposes no public listening ports; server mode rejects wildcard/global binds.
- [ ] Hermes + Codex OAuth has a documented successful clean-install smoke test on every supported OS family.
- [ ] Hindsight retain/recall/reflect passes an automated integration smoke test.
- [ ] Multi-device memory passes an actual two-client private-tailnet smoke test.
- [ ] Backup export + encrypted cloud copy + isolated test restore succeeds end-to-end.
- [ ] Every enabled MCP has documented trust level and effective tool surface.
- [ ] Every bundled/community skill has source/license/review metadata.
- [x] CI validates Python/shell/PowerShell syntax, configuration, privacy invariants, secret hygiene and site integrity.
- [x] Documentation includes install, uninstall, upgrade, backup/restore, privacy and threat model.
- [ ] Stable releases use pinned/tested service images and publish provenance/SBOM/security scan results.

## Future experiments (post-1.0)

- [ ] Optional OpenViking-as-primary-memory profile for users who prefer hierarchical context over Hindsight.
- [ ] Supermemory local-mode compatibility profile.
- [ ] ByteRover coding-only memory profile.
- [ ] Federated read-only memory search across multiple Hindsight banks.
- [ ] Local voice/STT/TTS profile.
- [ ] Private mobile/remote gateway profile.
- [ ] SOPS/age-managed declarative secrets for advanced users.
- [ ] Nix/Home Manager and Dev Container installers.
- [ ] Unraid Community Applications template.
