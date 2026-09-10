# Nango Free Self-Hosted

Nango is an optional credential-management and authenticated API-proxy layer for Hermes Privacy Stack.

It is included as an **alternative to Composio for authentication/proxying**, not as a replacement for Activepieces. The two tools solve different parts of the integration problem:

| Component | Best use in this stack |
|---|---|
| Nango Free Self-Hosted | OAuth/API-key connections, token refresh, encrypted credential storage, authenticated API proxy |
| Activepieces | No/low-code application workflows and connector actions |
| Hermes MCP/skills | Agent-facing tools with the narrowest useful authority |
| Windmill (planned) | Deterministic code-heavy workflows |

## Important feature boundary

As of September 2026, Nango documents two self-hosting tiers.

The **free self-hosted** edition is intended for lightweight Auth + Proxy use. It does **not** include the full functions runtime, webhooks, Nango-managed MCP server, role-based permissions, SAML, or full observability. Those capabilities belong to Nango Cloud / Enterprise Self-Hosted.

Hermes Privacy Stack therefore does not depend on any of those paid/runtime features. The optional local integration consists of:

- Nango server,
- a private Postgres database,
- Nango Connect UI,
- encrypted credential storage,
- the authenticated Nango Proxy API,
- a local Hermes proxy helper/skill.

Nango's source is available under the Elastic License 2.0. Review the upstream license before redistributing or offering it as a managed service.

## Install

After the base Hermes Privacy Stack install:

```bash
python scripts/setup_nango.py
```

Fresh interactive installs also offer Nango during the guided setup stage.

The script:

1. reads the existing local/server bind address,
2. generates a base64 256-bit `NANGO_ENCRYPTION_KEY`,
3. generates a Postgres password,
4. generates a dashboard password,
5. stores those values only in the private stack state file,
6. enables Nango's documented SSRF protections,
7. disables optional Nango telemetry and Elasticsearch logging,
8. starts the `nango` Compose profile,
9. installs the reviewed local `nango-proxy` Hermes skill.

No provider OAuth credentials are requested by this repository.

### Generate configuration without starting containers

```bash
python scripts/setup_nango.py --no-start
```

### Show the locally stored dashboard credentials

```bash
python scripts/setup_nango.py --show-credentials
```

This prints a secret to your terminal. Use it only when needed.

## Ports

Default local mode:

| Port | Purpose |
|---:|---|
| `3003` | Nango API + dashboard |
| `3009` | Nango Connect UI |
| Postgres | Docker-private only; not published to the host |

Both published ports bind to the same `HPS_BIND_ADDRESS` used by the rest of Hermes Privacy Stack. Local mode therefore binds to `127.0.0.1`; server mode binds to one explicitly selected private/overlay address.

Never publish the Postgres service.

## OAuth callback URL

Nango builds OAuth callbacks from `NANGO_SERVER_URL`:

```text
<NANGO_SERVER_URL>/oauth/callback
```

For localhost testing, the generated default is:

```text
http://localhost:3003
```

For a private overlay server it defaults to that private address. This is enough to administer Nango from trusted devices, but many OAuth providers require an HTTPS callback domain for non-localhost production applications.

When that applies, place Nango behind a trusted HTTPS reverse proxy/ingress and rerun:

```bash
python scripts/setup_nango.py --server-url https://nango.example.com
```

If Connect UI uses a different externally reachable origin, also pass:

```bash
--connect-url https://connect.example.com
```

Do not expose Hindsight, SearXNG, Docling, or other Hermes services merely because the Nango OAuth callback needs public HTTPS. Keep those services on loopback/private-overlay addresses.

## Dashboard security

The profile generates a unique dashboard password and configures Nango's dashboard credentials. The password is stored in the stack runtime environment outside Git.

The Nango encryption key protects sensitive database values. Upstream currently warns that this key cannot be rotated in place without breaking decryption, so:

- back it up in your encrypted disaster-recovery material,
- never commit it,
- never regenerate it on an existing database,
- never share it with an agent or external service.

`setup_nango.py` preserves an existing key/password on reruns.

## Provider credentials

Configure integrations inside Nango.

For OAuth providers, use your own OAuth application/client for production wherever practical. Shared/test OAuth applications are useful for development but should not become the permanent credential boundary for a private production stack.

Apply the smallest OAuth scopes that satisfy the workflow.

Examples:

```text
Drive read workflow       -> read-only Drive scope where provider supports it
Calendar lookup           -> calendar read scope
GitHub research           -> read-only repository/user scopes
GitHub automation         -> separate connection/key with write scopes
```

Prefer separate Nango integration configurations for materially different privilege levels.

## Hermes integration without paid Nango MCP

The free self-hosted edition does not include Nango's managed MCP server. Hermes Privacy Stack instead provides:

```bash
python scripts/nango_proxy.py
```

The helper calls the local/private Nango `/proxy/...` API and lets Nango inject the real provider credential.

Create a Nango API key with only the `environment:proxy` scope, then store it locally in the Hermes `.env`:

```text
NANGO_PROXY_TOKEN=<local Nango proxy-scoped API key>
```

Do **not** commit this value.

If your Nango server is not the local default, also set:

```text
NANGO_HOSTPORT=https://nango.example.com
```

### Read example

```bash
python scripts/nango_proxy.py \
  --provider github \
  --connection personal-github \
  --path /user
```

The helper sends:

```text
Authorization: Bearer <Nango proxy-scoped key>
Provider-Config-Key: <integration id>
Connection-Id: <connection id>
```

Nango then handles the provider's actual access token.

### Write example

State-changing methods are blocked unless `--allow-write` is supplied:

```bash
python scripts/nango_proxy.py \
  --provider example \
  --connection account-1 \
  --method POST \
  --path /resource \
  --body '{"name":"value"}' \
  --allow-write
```

The bundled Hermes skill instructs the agent to obtain explicit user approval before using that flag.

The helper intentionally does not expose Nango's `Base-Url-Override` or arbitrary passthrough headers by default. That keeps its authority smaller and reduces SSRF/confused-deputy risk.

## SSRF hardening

The Compose profile explicitly keeps Nango's base-URL override protection enabled and applies an outbound policy that blocks private IP targets for ordinary proxy calls and limits redirects.

This matters because an authenticated proxy can otherwise become a route from an agent to internal metadata services or other private endpoints.

If you genuinely need Nango to proxy a private/internal API, review the threat model first and override the policy deliberately rather than disabling it globally.

## Logs and telemetry

The lightweight profile sets:

```text
NANGO_LOGS_ENABLED=false
NANGO_TELEMETRY_SDK=false
TELEMETRY=false
```

Elasticsearch is not started.

Container stdout can still contain operational metadata, provider names, paths, and errors. Treat Docker logs as potentially sensitive.

## Backups

Nango's durable data lives in:

- `nango_db_data` Docker volume,
- the generated encryption key in the private stack environment.

A database backup without the matching encryption key may be unusable for encrypted credentials.

Before Nango is considered production-ready in this project, the backup tooling should gain a logical `pg_dump`/restore path and an isolated restore drill. This is tracked in the roadmap.

## ARM64 / Apple Silicon

Nango's current upstream free Docker Compose example explicitly targets `linux/amd64` for the server image. The stack mirrors that as the default `HPS_NANGO_PLATFORM`.

On Apple Silicon/ARM64 this may therefore run under Docker emulation and be slower. Override the platform only after confirming the selected Nango image publishes a compatible native manifest.

## Uninstall

Stop only the Nango profile:

```bash
docker compose \
  --env-file ~/.hermes-privacy-stack-state/stack.env \
  -f stack/compose.yml \
  --profile nango \
  down
```

Do **not** add `-v` unless you intend to destroy Nango's database.

To permanently remove it, first export any connection/configuration information you need, remove the `nango_db_data` volume, and then delete the local `HPS_NANGO_*` values from the stack state file.

## Upstream references

- Nango self-hosting guide: https://nango.dev/docs/guides/platform/self-hosting
- Nango repository: https://github.com/NangoHQ/nango
- Proxy API: https://nango.dev/docs/guides/platform/proxy-requests
- Pricing / feature boundaries: https://nango.dev/pricing
