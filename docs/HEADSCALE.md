# Headscale for Hermes Privacy Stack

Headscale is the supported self-hosted mesh-coordination option for strict-free v2. Compatible Tailscale client software can connect to your Headscale control server while the coordination/control plane remains under your control.

## Architecture

```text
Internet
   │
   ▼
self-hosted Headscale coordination endpoint
   │
   └── compatible clients enrolled with --login-server ──────┐
                                                              │
                                            ┌─────────────────▼──┐
                                            │ Hermes server       │
                                            │ private mesh IP     │
                                            │ memory   :8765      │
                                            │ SearXNG  :8088      │
                                            │ Docling  :5001      │
                                            └──────────┬──────────┘
                                                       │
                                               approved clients
```

Only the Headscale coordination endpoint needs Internet reachability for roaming clients. Hermes services should remain bound to their private mesh address.

## Deploy Headscale

Use a versioned official Headscale release/container and the configuration matching that exact version. Stable deployments should not rely on a mutable `latest` tag.

Headscale generally needs a stable HTTPS URL for roaming devices. The planned Caddy edge helper will automate this later; until then, follow Headscale's official reverse-proxy/TLS guidance.

## Create a user

Native:

```bash
headscale users create hermes
```

Container deployment example:

```bash
podman exec -it headscale headscale users create hermes
```

(`docker exec` is equivalent for Docker users.)

## Enroll the Hermes server

Install compatible client software, then point it at your Headscale server:

```bash
tailscale up --login-server https://headscale.example.com
```

Retrieve the mesh IPv4:

```bash
tailscale ip -4
```

Verify the client is actually using **your Headscale control server**. `scripts/private_network.py` can detect the address but cannot prove the enrollment/control-plane identity.

Bind the stack to the exact address:

```bash
./install.sh \
  --role server \
  --bind-address 100.64.20.30 \
  --model-provider skip
```

## Enroll clients

Enroll trusted machines against the same Headscale server, then configure client mode:

```bash
MCP_MEMORY_API_KEY='...' \
./install.sh \
  --role client \
  --memory-url http://100.64.20.30:8765 \
  --searxng-url http://100.64.20.30:8088 \
  --model-provider chatgpt-oauth
```

The memory key should be transferred using a password/secret manager rather than copied into shell scripts.

## Least-privilege policy

A private IP does not equal least privilege. Load an explicit Headscale policy rather than assuming every enrolled device should reach every service.

Conceptual ordinary-client access:

```text
TCP 8765   mcp-memory-service
TCP 8088   SearXNG
TCP 5001   Docling (only if direct document service access is needed)
```

Researcher profile may additionally need:

```text
TCP 11235  Crawl4AI
```

Operator/admin devices may additionally receive:

```text
TCP 1880   Node-RED
TCP 3000   Forgejo HTTP
TCP 2222   Forgejo SSH
```

Remote llama.cpp inference is optional:

```text
TCP 8080   llama.cpp
```

Do not grant `*` merely to make setup easier.

## Grants example

Headscale supports Tailscale-compatible policy syntax. A conceptual grant can restrict one client to only memory and search:

```json
{
  "grants": [
    {
      "src": ["100.64.20.40"],
      "dst": ["100.64.20.30"],
      "ip": ["tcp:8765", "tcp:8088"]
    }
  ]
}
```

Treat this as a pattern, not a copy/paste guarantee across Headscale versions. Validate against the policy documentation for the exact release you deploy. For larger setups, prefer durable groups/tags over many hard-coded IP rules.

## DNS

Human-readable private DNS names can be convenient for client URLs. The stack itself still binds services to an exact private IP so a DNS change cannot accidentally move a listener onto another interface.

## Headscale vs plain WireGuard

Choose Headscale when:

- devices roam between networks,
- you want easier peer discovery/enrollment,
- you expect more than a few clients,
- you are comfortable operating a coordination endpoint.

Choose plain WireGuard/wg-easy when:

- topology is small and stable,
- minimal moving parts matter more than mesh convenience,
- manual peer configuration is acceptable.

Both satisfy the strict-free architecture when fully self-hosted.

## Upstream references

- https://headscale.net/stable/usage/getting-started/
- https://headscale.net/stable/setup/install/container/
- https://headscale.net/stable/ref/policy/
