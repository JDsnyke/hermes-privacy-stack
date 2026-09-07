# Roadmap

This file is both the product plan and the implementation tracker. Keep it current as features land. Items marked **P0** block a privacy-first 1.0 release.

Legend: `[x]` complete · `[-]` partial/in progress · `[ ]` planned.

## Release target: v0.1 foundation

### P0 — privacy and repository safety

- [ ] **Make GitHub repository private** (GitHub currently reports it as public). If intentionally public, keep the public-safe policy permanently.
- [x] Add strict `.gitignore` for credentials, OAuth state, memories, sessions, databases, caches and backups.
- [x] Add `SECURITY.md` with loopback/private-network and MCP/skill trust rules.
- [x] Add CI secret-pattern scanner and forbidden-runtime-file checks.
- [x] Keep GitHub Pages static, dependency-free and analytics-free.
- [ ] Add release signing / provenance (GitHub attestations or Sigstore) for installer tags.
- [ ] Pin container images by version/digest for stable releases; keep `latest` only on edge/dev channel.
- [ ] Add SBOM generation for release artifacts.

### P0 — installer reliability

- [x] Cross-platform shell/PowerShell entrypoints.
- [x] Python bootstrap wizard with presets and local/server/client roles.
- [x] Use official Hermes installer rather than vendoring Hermes.
- [x] Keep Codex OAuth configuration inside Hermes' own model setup.
- [x] Detect Docker/Git/Python/Hermes and provide actionable failures.
- [ ] Full native-Windows smoke test.
- [ ] macOS Intel + Apple Silicon smoke test.
- [ ] Linux x86_64 + ARM64 smoke test.
- [ ] WSL2 smoke test.
- [ ] Idempotent upgrade test: run installer twice without overwriting user-owned data.
- [ ] Automated rollback snapshot before config changes.

## v0.2 — core local stack

### Memory

- [x] Hindsight as recommended external memory provider.
- [x] External-server topology for multi-device memory.
- [x] `hermes-{profile}` bank template guidance.
- [x] Local Ollama service reserved for auxiliary memory inference.
- [ ] Verify Hindsight's current Ollama structured-output model compatibility on every release.
- [ ] Add optional Hindsight `openai-codex` auxiliary provider path for users who prefer no local model.
- [ ] Add bank mission/disposition presets for personal, coding and research profiles.
- [ ] Add scripted bank health check, stats and backup validation.

### Search / research

- [x] SearXNG default search service.
- [x] Privacy-oriented SearXNG configuration template.
- [ ] Confirm Hermes `SEARXNG_URL` path automatically during install.
- [ ] Add optional self-hosted Firecrawl installer using upstream pinned release.
- [ ] Add Crawl4AI alternative profile and comparison.
- [ ] Add research skill that selects browser vs Firecrawl vs Docling based on task.

### Documents

- [x] Docling service placeholder/profile and document-intake skill.
- [ ] Pin/test Docling serve/MCP invocation against upstream release.
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
- [ ] Automated Activepieces community install using upstream installer or pinned Compose.
- [ ] Generate Hermes MCP config from selected catalog entries.
- [ ] Add per-tool allowlist generator.
- [ ] Add ToolHive optional isolation/gateway layer when MCP count exceeds threshold.
- [ ] Add Windmill optional code-workflow layer.
- [ ] Add Google Workspace setup guide (Gmail/Calendar/Drive) through Activepieces with minimal OAuth scopes.
- [ ] Add GitHub MCP write profile separate from read-only profile.

## v0.4 — skills and personalities

- [x] Built-in privacy-audit, memory-hygiene, document-intake, research-pipeline, multi-instance-sync and backup-restore skills.
- [x] Curated third-party skill catalog design (review before install).
- [ ] Add source hashing + review metadata for third-party skill pins.
- [ ] Add skill installer that stages source for diff/review before enabling.
- [ ] Add popular coding/research skill profiles after security review.
- [x] Starter `SOUL.md` and user-safe profile templates.
- [ ] Interactive personality builder with preview/diff before writing.
- [ ] Optional `coder`, `researcher`, `operator`, `private-personal` profile bundles.
- [ ] Per-profile memory retention policies.

## v0.5 — multi-device and backup

- [x] Authoritative Hindsight server + private-tailnet design.
- [x] Explicit prohibition on syncing live DB files.
- [ ] Tailscale helper that advertises only selected service ports.
- [ ] Hindsight logical bank export/import backup scripts using current `hindsight-admin export-bank` / `import-bank`.
- [ ] Restic encrypted backup backend.
- [ ] rclone crypt backend for Google Drive / OneDrive / S3-compatible free tiers.
- [ ] Optional Syncthing for *non-database* Obsidian/knowledge files.
- [ ] Rotation policy: daily/weekly/monthly snapshots with retention limits.
- [ ] Disaster-recovery drill script that restores into a temporary bank and tests recall.
- [ ] Optional OpenViking central server + per-client MCP routing over tailnet.

## v0.6 — interactive UX

- [x] Static interactive site with no third-party JS/CSS/fonts.
- [x] Animated architecture visualization.
- [x] Preset/config command generator.
- [ ] PWA/offline documentation.
- [ ] Service dependency graph with live local health import (explicit opt-in; browser-local only).
- [ ] Export generated config as a local JSON download without transmitting it.
- [ ] Interactive threat-model wizard.
- [ ] Dark/light theme persisted locally.
- [x] GitHub Pages deploy workflow and documented private/public mirror options.
- [ ] Enable GitHub Pages for this repository with **Settings → Pages → Source: GitHub Actions**; current workflow cannot deploy until the Pages site is enabled.

## v0.7 — observability and maintenance

- [x] Local `doctor.py` skeleton for component health.
- [x] Structured doctor output (`--json`) for support bundles.
- [ ] Optional self-hosted Langfuse plugin profile, disabled by default.
- [ ] Dependency update bot with human review and release notes.
- [ ] Container vulnerability scanning in CI.
- [ ] Backup freshness and memory-server health cron examples.
- [ ] One-command safe update with preflight + rollback.

## v1.0 acceptance criteria

A release can be tagged 1.0 only when:

- [ ] Installer passes Windows native, WSL2, macOS Intel, macOS ARM64, Linux x86_64 and Linux ARM64 tests.
- [ ] No secrets or personal state are required in Git.
- [ ] Default stack exposes no public listening ports.
- [ ] Hermes + Codex OAuth works before optional services are installed.
- [ ] Hindsight retain/recall/reflect passes local smoke tests.
- [ ] Multi-device memory works over a private tailnet.
- [ ] Backup export + encrypted cloud copy + test restore succeeds.
- [ ] Every enabled MCP has a documented trust level and tool surface.
- [ ] Every bundled/community skill has source/license/review metadata.
- [ ] CI validates syntax, configuration, secret hygiene and site integrity.
- [ ] Documentation includes install, uninstall, upgrade, restore and threat model.

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
