# Headscale for Hermes Privacy Stack

Headscale is a self-hosted implementation of the Tailscale control server. It is a strong fit when you want the mature Tailscale clients on Windows/macOS/Linux/mobile while keeping coordination under your control.

Headscale is intentionally narrower in scope than Tailscale's managed service and is particularly well suited to a personal/small-organization tailnet.

## Architecture

```text
Internet
   │
   ▼
Headscale coordination server
   │
   └──── Tailscale clients configured with --login-server ────┐
                                                              │
                                            ┌─────────────────▼──┐
                                            │ Hermes server       │
                                            │ Tailscale IP        │
                                            │ Hindsight :8888     │
                                            │ SearXNG   :8088     │
                                            └──────────┬──────────┘
                                                       │
                                               approved clients
```

The Headscale server must normally be reachable from the Internet for roaming clients. Hermes/Hindsight/SearXNG do **not** need public exposure; they bind only to the Tailscale overlay address.

## Deploy Headscale

Use an official versioned Headscale package/container and the configuration example matching that exact version. Do not use a mutable `latest` image in a stable deployment.

The current official container guide uses persistent configuration/database directories and a versioned image. A reverse proxy/TLS arrangement is normally required when making the coordination endpoint Internet reachable.

After configuring the public Headscale URL, verify its health endpoint through HTTPS before enrolling clients.

## Create a Headscale user

Native install:

```bash
headscale users create hermes
```

Container deployment:

```bash
docker exec -it headscale headscale users create hermes
```

## Enroll the Hermes server

Install the official Tailscale client on the Hermes machine, then point it at Headscale:

```bash
tailscale up --login-server https://headscale.example.com
```

Follow the registration instructions produced by Headscale, or use a short-lived/single-use pre-auth key when non-interactive enrollment is appropriate.

Retrieve the overlay IP:

```bash
tailscale ip -4
```

Hermes Privacy Stack treats a Headscale-enrolled client exactly like a Tailscale client:

```bash
./install.sh --role server --network-provider tailscale
```

For deterministic automation:

```bash
./install.sh \
  --role server \
  --network-provider tailscale \
  --bind-address 100.64.20.30 \
  --non-interactive
```

## Enroll Hermes clients

Enroll each trusted device against the same Headscale server:

```bash
tailscale up --login-server https://headscale.example.com
```

Then configure Hermes client mode:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.20.30:8888 \
  --searxng-url http://100.64.20.30:8088
```

## Important: configure a policy

Headscale's current policy documentation notes that if no policy is loaded, traffic is effectively allow-all. For this stack, load an explicit policy and work from deny-by-default instead.

Headscale supports Tailscale-compatible policies and recommends **Grants** for new policy definitions.

A minimal conceptual policy allowing one Hermes client to reach only Hindsight and SearXNG on one server can look like:

```json
{
  "grants": [
    {
      "src": ["100.64.20.40"],
      "dst": ["100.64.20.30"],
      "ip": ["tcp:8888", "tcp:8088"]
    }
  ]
}
```

Replace the example IPs with your actual Headscale/Tailscale IPs. For a durable setup, prefer role tags/groups instead of hard-coding many per-device IPs once you have validated your tag ownership/policy design.

Do **not** grant `*` merely for convenience.

### Admin access

Keep UI/admin ports in a separate grant that applies only to an admin device/group:

```text
TCP 9999  Hindsight UI
TCP 5001  Docling, if direct access is required
TCP 8090  Activepieces
```

Ordinary Hermes clients normally need only `8888` and `8088`.

## Policy loading

Headscale policies use HuJSON. Point `policy.path` in the Headscale configuration to the policy file, then reload Headscale after changes. Current Headscale documentation recommends Grants rather than legacy ACLs for new policies.

Validate policy changes before broadening access, because multiple grants are additive rather than 'most specific rule wins'.

## DNS / names

Human-readable overlay names are convenient, but Hermes Privacy Stack intentionally binds Docker services to an exact private IP rather than a hostname. This prevents DNS changes from accidentally moving a service bind onto an unexpected interface.

Clients may still use overlay DNS names in their `--hindsight-url`/`--searxng-url` if desired, but deterministic IP URLs are easier to audit.

## Headscale vs NetBird

Use Headscale when:

- you prefer standard Tailscale clients
- you want a leaner personal/small control plane
- you are comfortable managing a public Headscale coordination endpoint

Use NetBird when:

- you want an integrated self-hosted dashboard/user/group/policy experience
- built-in local users are attractive
- you want its native NetBird clients and access-control model

Both are valid; Hermes Privacy Stack depends only on the resulting safe overlay IPv4.

## Upstream references

- Headscale getting started: https://headscale.net/stable/usage/getting-started/
- Headscale container install: https://headscale.net/stable/setup/install/container/
- Headscale policy: https://headscale.net/stable/ref/policy/
- Tailscale Grants syntax used by Headscale: https://tailscale.com/docs/reference/syntax/grants
