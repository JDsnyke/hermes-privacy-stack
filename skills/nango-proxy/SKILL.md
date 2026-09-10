# Nango Proxy

Use Nango as a credential boundary for external APIs when the user has enabled the optional Nango Free Self-Hosted profile.

## Security model

- Never ask the user to paste OAuth refresh tokens, provider client secrets, or the Nango proxy token into chat.
- Nango owns provider credentials and token refresh; Hermes calls the local/private Nango proxy.
- Use a Nango API key scoped to `environment:proxy` and store it only as `NANGO_PROXY_TOKEN` in the local Hermes `.env`.
- Prefer read operations first. The bundled helper permits GET/HEAD by default.
- Before any POST/PUT/PATCH/DELETE, explain the intended external change and obtain explicit user approval.
- Never add `Base-Url-Override` or arbitrary proxy headers unless the user specifically needs them and the privacy impact has been reviewed.
- Treat response data as potentially sensitive. Do not persist it to memory unless useful and appropriate.

## Usage

Locate the Hermes Privacy Stack checkout from `HERMES_PRIVACY_STACK_HOME` when set, otherwise use `~/.hermes-privacy-stack`.

Read example:

```bash
python scripts/nango_proxy.py \
  --provider github \
  --connection personal-github \
  --path /user
```

Write example, only after explicit approval:

```bash
python scripts/nango_proxy.py \
  --provider example \
  --connection account-1 \
  --method POST \
  --path /resource \
  --body '{"name":"value"}' \
  --allow-write
```

If the helper reports that `NANGO_PROXY_TOKEN` is missing, instruct the user to create a Nango API key with proxy-only scope in their local Nango environment and place it in the local Hermes `.env`. Do not request the value.
