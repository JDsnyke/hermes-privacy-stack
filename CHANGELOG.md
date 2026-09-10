# Changelog

All notable changes to Hermes Privacy Stack are tracked here. Until the first stable release, entries live under **Unreleased** and `ROADMAP.md` remains the implementation-status source of truth.

## Unreleased

### Security / privacy hardening

- Explicitly pin Hermes web search to self-hosted SearXNG and disable keyless fallback/rescue.
- Reject wildcard and globally routable service bind addresses; shared-server mode uses a specific private/overlay IP.
- Generate SearXNG secret keys at install time outside Git.
- Remove automatic OpenViking startup until authenticated root-key/model provisioning exists.
- Add a detailed threat model, privacy review rules, privacy-safe issue forms and PR checklist.
- Add redacted diagnostic output for support reports.
- Add Nango Free Self-Hosted as an optional credential boundary with generated encryption/database/dashboard secrets outside Git, Docker-private Postgres, SSRF protections and telemetry/log-storage opt-outs.
- Add a least-authority Nango Proxy helper that never accepts its API token on the command line, defaults to read-only methods and requires an explicit write gate for state-changing requests.

### Installer / multi-device

- Harden local/server/client roles and require both Hindsight and SearXNG URLs for non-interactive clients.
- Add provider-agnostic private-network detection for NetBird and Tailscale/Headscale plus documented policy/port guidance.
- Add runtime state under a machine-local directory instead of the repository checkout.
- Add pre-configuration Hermes quick backup and installer privacy self-test.
- Add guided optional Nango setup while preserving existing Nango encryption/database/dashboard secrets on reruns.

### Integrations

- Keep Activepieces as the optional visual workflow layer.
- Add Nango Free Self-Hosted as an optional Composio alternative for **Auth + Proxy** rather than claiming Nango Cloud/Enterprise functions, webhooks or managed MCP features.
- Add the reviewed `nango-proxy` Hermes skill and `scripts/nango_proxy.py` for proxy-scoped API access.
- Add a disposable Nango container integration workflow covering API health, Connect UI, loopback binding, private Postgres exposure and secret idempotency.

### Memory / backup

- Correct Hindsight → Ollama URL to the OpenAI-compatible `/v1` endpoint.
- Add logical `hindsight-admin export-bank` / `import-bank` helpers.
- Add sanitized config backups, full native Hermes backup delegation, SHA-256 manifests and safe restore tooling.
- Add optional rclone copy to an explicitly confirmed `crypt` destination.

### Maintenance / CI

- Add Windows/macOS/Linux bootstrap self-test matrix.
- Add twice-run bootstrap idempotency validation preserving user-owned SOUL/USER/auth/config/private env material and generated SearXNG secrets.
- Validate Nango setup/proxy invariants on Windows, macOS and Linux and validate the optional Nango Compose profile without real credentials.
- Extend image-lock/supply-chain coverage to Nango Server and its Postgres image using in-memory non-secret Compose placeholders.
- Validate PowerShell, shell, Python, JSON, YAML, Compose and static-site privacy invariants.
- Replace the primitive updater with dirty-tree refusal, pre-backup, pre/post validation and automatic repository rollback.
- Keep Docker service-image and Hermes-agent updates separate explicit operations.
- Gate GitHub Pages deployment until explicitly enabled.

### Documentation

- Add/update quick start, multi-device memory, NetBird/Headscale/Tailscale, backup/restore, safe upgrades, uninstall, services, privacy, Pages and threat-model documentation.
- Add a dedicated Nango runbook covering free self-host feature boundaries, OAuth callback/HTTPS design, credentials/scopes, Proxy API use, SSRF protection, logs, backup constraints and ARM64 caveats.
- Reconcile `README.md` and `ROADMAP.md` with the actual hardened architecture.
