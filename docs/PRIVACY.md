# Privacy principles

See [THREAT-MODEL.md](THREAT-MODEL.md) for the detailed threat model. This page defines the operational defaults.

## Protected assets

- OAuth refresh/access tokens
- API keys and connector tokens
- user profile (`USER.md`) and memories
- conversation/session history
- files ingested for research/document work
- Activepieces/OpenViking connection secrets
- browser cookies/session state
- backup encryption keys and archives

## Defaults

### Local first

Core services bind to `127.0.0.1` by default. `server` mode accepts only a specific loopback/private/Tailscale IP and rejects `0.0.0.0`, `::` and globally routable addresses.

### Fail closed web search

Hermes is explicitly configured with:

```yaml
web:
  search_backend: searxng
  keyless_fallback: false
  keyless_rescue: false
```

If the private search service fails, the desired behavior is an error—not silently transmitting the query to an anonymous free-tier provider.

### Runtime secrets outside Git

The installer writes machine-local state outside the repository:

- generated Compose env
- SearXNG secret key/runtime config
- topology/install metadata
- backup bundles

Git stores templates and reviewed defaults only.

### Least authority

- no automatic community-skill installation,
- no automatic high-authority MCP,
- built-in Hermes memory writes require approval in the distributed profile,
- optional integration layers are disabled unless selected,
- OpenViking is not auto-started until authenticated runtime provisioning is implemented.

### No live database sync

Hindsight/Hermes databases are never synchronized through Drive/Dropbox/Syncthing. Multi-device memory uses the Hindsight API; backups use logical export/import.

### Cloud storage only after encryption

Google Drive/OneDrive/S3-compatible storage may be used for encrypted backup objects. The backup helper only copies to rclone when the user explicitly confirms the destination is a crypt remote.

## Baseline host security

This project cannot make a compromised host safe. Use full-disk encryption, OS updates, screen lock, MFA/passkeys, secure boot where practical, and a hardware-backed credential store/password manager for long-lived secrets.

## Privacy review rule

Every new service/MCP/skill should answer:

1. What data can it read?
2. What can it write/delete/send?
3. Which ports/processes does it expose?
4. Which credentials/scopes does it require?
5. Does data leave the device/tailnet?
6. What happens when it fails?
7. Can the same job be done with less authority?
