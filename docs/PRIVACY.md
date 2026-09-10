# Privacy principles

See [THREAT-MODEL.md](THREAT-MODEL.md) for the detailed threat model. This page defines the operational defaults.

## Protected assets

- OAuth refresh/access tokens
- API keys and connector tokens
- Nango encryption key, dashboard credentials, proxy-scoped keys and provider connections
- user profile (`USER.md`) and memories
- conversation/session history
- files ingested for research/document work
- Activepieces/OpenViking connection secrets
- browser cookies/session state
- backup encryption keys and archives

## Defaults

### Local first

Core services bind to `127.0.0.1` by default. `server` mode accepts only a specific loopback/private/overlay IP and rejects `0.0.0.0`, `::` and globally routable addresses.

Optional Nango follows the same host bind. Its Postgres database is not published to a host port.

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

The installer/setup helpers write machine-local state outside the repository:

- generated Compose env
- SearXNG secret key/runtime config
- optional Nango encryption/database/dashboard secrets
- topology/install metadata
- backup bundles

Git stores templates and reviewed defaults only.

### Credential separation

When Nango is enabled, treat it as a credential boundary rather than a convenience database.

- Provider OAuth refresh tokens and API credentials stay in Nango rather than being copied into Hermes.
- Hermes receives only a Nango proxy key with the narrowest useful scope, preferably `environment:proxy`.
- The bundled Nango helper accepts its proxy key only from local environment/config, never as a command-line argument.
- Read methods are the default. State-changing methods require an explicit write flag after user approval.
- Nango's database and `NANGO_ENCRYPTION_KEY` are a recovery pair; protect and back them up together.
- A public HTTPS OAuth callback for Nango must not expose Hindsight, SearXNG, Docling or the rest of the private stack.

### Least authority

- no automatic community-skill installation,
- no automatic high-authority MCP,
- built-in Hermes memory/skill writes can require approval,
- optional integration layers are disabled unless selected,
- Nango Proxy uses a read-first helper with an explicit write gate,
- OpenViking is not auto-started until authenticated runtime provisioning is implemented.

### Outbound proxy hardening

An authenticated API proxy can become an SSRF/confused-deputy path. The Nango profile keeps base-URL override protections enabled, blocks private-IP outbound targets by default and limits redirects. Do not disable these controls globally just to reach one internal API; design a narrow exception or a dedicated integration instead.

### No live database sync

Hindsight/Hermes/Nango databases are never synchronized through Drive/Dropbox/Syncthing. Multi-device memory uses the Hindsight API; backups use logical export/import. Nango will use a logical Postgres backup path once its release hardening in issue #6 is complete.

### Cloud storage only after encryption

Google Drive/OneDrive/S3-compatible storage may be used for encrypted backup objects. The backup helper only copies to rclone when the user explicitly confirms the destination is a crypt remote.

## Baseline host security

This project cannot make a compromised host safe. Use full-disk encryption, OS updates, screen lock, MFA/passkeys, secure boot where practical, and a hardware-backed credential store/password manager for long-lived secrets.

## Privacy review rule

Every new service/MCP/skill/credential broker should answer:

1. What data can it read?
2. What can it write/delete/send?
3. Which ports/processes does it expose?
4. Which credentials/scopes does it require?
5. Does data leave the device/private overlay?
6. What happens when it fails?
7. Can the same job be done with less authority?
8. How is its encrypted/secret-bearing state backed up and restored?
