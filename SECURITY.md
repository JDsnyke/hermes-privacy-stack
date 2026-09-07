# Security policy

Privacy is the primary design constraint of this repository.

## Non-negotiable rules

1. Never commit Hermes/Codex OAuth state, `.env`, API keys, rclone credentials, Tailscale auth keys, Activepieces connection secrets, service databases, `USER.md`, memories or sessions.
2. Bind services to loopback by default. Multi-device access should use Tailscale/WireGuard or another authenticated private network.
3. Never cloud-sync live SQLite/PostgreSQL/Hindsight/OpenViking database files.
4. Treat skills, MCP servers and browser extensions as executable code. Review source and pin versions for anything with write access.
5. High-authority MCP operations (email send, calendar writes, GitHub writes, shell/filesystem writes) must be opt-in and should have explicit tool allowlists.
6. Encrypt memory/config backups client-side before storing them in Google Drive or other cloud storage.
7. Do not expose Firecrawl, Hindsight, Docling, OpenViking, Ollama or Activepieces directly to the public Internet without authentication, TLS, rate limiting and an explicit threat model.

## Public-repository safety

The repository contains templates only. CI scans common secret patterns and rejects runtime/private files. This is defense in depth, not a substitute for keeping the intended repository private.

## Reporting

Create a private security issue if possible. If a secret was committed, assume compromise: revoke/rotate it immediately and remove it from Git history before relying on repository privacy.
