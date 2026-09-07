# Privacy and threat model

## Protected assets

- OAuth refresh/access tokens
- API keys and connector tokens
- User profile (`USER.md`) and memories
- Conversation/session history
- Files ingested for research/document work
- Activepieces connection secrets
- Browser cookies/session state
- Backup encryption keys

## Default adversaries considered

- Accidental Git commit or public repo exposure
- Over-privileged MCP/skills
- A compromised external website reached by the browser
- Cloud storage provider seeing backup contents
- Another device on the LAN
- Container/service accidentally exposed on all interfaces

## Defaults

- Loopback binds only.
- No analytics or third-party assets on the Pages site.
- No automatic community-skill installation.
- No automatic high-authority MCP.
- No live DB file sync.
- OAuth remains under the upstream client's auth storage.

## Not solved automatically

This project does not make a compromised host safe. Malware running as your user can likely access local tokens and data. Use full-disk encryption, OS updates, screen lock, account MFA and a hardware-backed credential store where possible.
