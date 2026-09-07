# Changelog

All notable changes to Hermes Privacy Stack are tracked here. Until the first stable release, entries live under **Unreleased** and `ROADMAP.md` remains the implementation-status source of truth.

## Unreleased

### Security / privacy hardening

- Explicitly pin Hermes web search to self-hosted SearXNG and disable keyless fallback/rescue.
- Reject wildcard and globally routable service bind addresses; shared-server mode uses a specific private/Tailscale IP.
- Generate SearXNG secret keys at install time outside Git.
- Remove automatic OpenViking startup until authenticated root-key/model provisioning exists.
- Add a detailed threat model, privacy review rules, privacy-safe issue forms and PR checklist.
- Add redacted diagnostic output for support reports.

### Installer / multi-device

- Harden local/server/client roles and require both Hindsight and SearXNG URLs for non-interactive clients.
- Add Tailscale-address auto-detection and documented ACL/port guidance.
- Add runtime state under a machine-local directory instead of the repository checkout.
- Add pre-configuration Hermes quick backup and installer privacy self-test.

### Memory / backup

- Correct Hindsight → Ollama URL to the OpenAI-compatible `/v1` endpoint.
- Add logical `hindsight-admin export-bank` / `import-bank` helpers.
- Add sanitized config backups, full native Hermes backup delegation, SHA-256 manifests and safe restore tooling.
- Add optional rclone copy to an explicitly confirmed `crypt` destination.

### Maintenance / CI

- Add Windows/macOS/Linux bootstrap self-test matrix.
- Validate PowerShell, shell, Python, JSON, YAML, Compose and static-site privacy invariants.
- Replace the primitive updater with dirty-tree refusal, pre-backup, pre/post validation and automatic repository rollback.
- Keep Docker service-image and Hermes-agent updates separate explicit operations.
- Gate GitHub Pages deployment until explicitly enabled.

### Documentation

- Add/update quick start, multi-device memory, Tailscale, backup/restore, safe upgrades, uninstall, services, privacy, Pages and threat-model documentation.
- Reconcile `README.md` and `ROADMAP.md` with the actual hardened architecture.
