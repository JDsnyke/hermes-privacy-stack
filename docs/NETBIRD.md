# NetBird self-hosted for Hermes Privacy Stack

NetBird is the recommended **complete self-hosted overlay** option when you want a WireGuard-based mesh, dashboard, user/device groups and granular access policy without depending on a managed Tailscale control plane.

This guide separates two very different things:

1. **NetBird control plane** — normally public/reachable so roaming peers can coordinate.
2. **Hermes service host** — Hindsight, SearXNG, Docling, etc. should remain private and bind only to the server's NetBird overlay IP.

Do not expose Hermes services through the public NetBird server just because both are self-hosted.

## Current upstream requirements

NetBird's self-hosted quickstart currently expects:

- a Linux VM with at least 1 CPU / 2 GB RAM
- Docker + Compose
- a public domain resolving to the VM
- inbound TCP 80/443 and UDP 3478 to the NetBird control-plane VM

Current NetBird releases also include built-in local user management through embedded Dex, so an external Keycloak/Zitadel/OIDC provider is optional rather than mandatory.

Always follow the current upstream self-hosted quickstart for the control plane rather than copying an old Compose file into this repository. The project intentionally avoids vendoring mutable authentication/network infrastructure.

## Recommended topology

```text
Internet
   │
   │  only NetBird coordination / relay endpoints
   ▼
NetBird control-plane VM
   │
   └──────────── encrypted NetBird overlay ──────────────┐
                                                         │
                                  ┌──────────────────────▼──┐
                                  │ Hermes service server   │
                                  │ NetBird IP: 100.x.y.z   │
                                  │                         │
                                  │ Hindsight      :8888    │
                                  │ SearXNG        :8088    │
                                  │ Hindsight UI   :9999    │
                                  │ Docling        :5001    │
                                  └──────────┬──────────────┘
                                             │
                           approved NetBird peers only
                                             │
                              laptop / desktop / server
```

The NetBird control plane and Hermes service host may technically be the same machine, but separating them is preferable when you have the resources because the former has deliberate Internet exposure while the latter contains private memory/data services.

## Join the Hermes server

Install the NetBird client using the current upstream instructions and enroll it in your self-hosted account.

Verify connectivity and retrieve the server overlay IPv4:

```bash
netbird status --ipv4
```

Hermes Privacy Stack can auto-detect that address:

```bash
python scripts/private_network.py
```

Install server mode using NetBird explicitly:

```bash
./install.sh --role server --network-provider netbird
```

For automation, explicitly passing the address is even more deterministic:

```bash
./install.sh \
  --role server \
  --network-provider netbird \
  --bind-address 100.100.20.30 \
  --non-interactive
```

The installer refuses wildcard/global bind addresses.

## Join Hermes clients

Install/enroll NetBird on each trusted client device. Then configure the Hermes client with the server's NetBird IP:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.100.20.30:8888 \
  --searxng-url http://100.100.20.30:8088
```

## Remove the default full-mesh policy

A new NetBird account may have a default policy that permits broad peer-to-peer connectivity. For a privacy-first Hermes deployment, do not treat membership in the overlay as sufficient authorization.

In the NetBird dashboard:

1. Create a peer/user group such as `hermes-clients` for devices allowed to use the agent services.
2. Create a destination peer group such as `hermes-server` containing only the machine hosting Hindsight/SearXNG.
3. Disable/remove the broad Default policy once you have tested replacement policies.
4. Create narrowly scoped access policies from `hermes-clients` → `hermes-server`.

NetBird policies support source groups, destination groups, protocol and specific ports/ranges.

## Suggested policy split

Do not make one rule granting all ports. Use separate rules so admin surfaces can be restricted independently.

### Ordinary Hermes clients

Source: `hermes-clients`  
Destination: `hermes-server`

Allow:

```text
TCP 8888  Hindsight API
TCP 8088  SearXNG
```

Add TCP 5001 only for clients that genuinely need direct Docling access.

### Admin devices

Create another source group such as `hermes-admins`.

Allow the ordinary client ports plus, only if needed:

```text
TCP 9999  Hindsight UI
TCP 5001  Docling
TCP 8090  Activepieces
```

This reduces lateral movement if a normal laptop is compromised.

## NetBird host firewall interaction

NetBird manages traffic on its WireGuard interface, but keep host firewalls enabled. The overlay policy should be the primary cross-peer authorization layer; the host firewall remains defense in depth.

Hermes Privacy Stack also binds Docker ports to the exact NetBird IP rather than `0.0.0.0`, so the services are not automatically exposed on Ethernet/Wi-Fi interfaces.

## Local users vs external identity provider

For a personal deployment, NetBird's built-in local user management is enough to avoid operating a separate identity service.

Consider an external IdP only when you need features such as organization-wide SSO, centralized identity lifecycle or existing Google/Microsoft/Okta integration. Keep MFA enabled wherever your chosen identity path supports it.

## Backups

Back up the NetBird control plane separately from Hermes memory. NetBird configuration/identity state and Hindsight memory are different trust domains and should not be merged into one unencrypted archive.

Hermes memory continues to use logical Hindsight exports:

```bash
python scripts/backup.py --bank hermes-default
```

## Troubleshooting

Check the server's detected overlay address:

```bash
netbird status --ipv4
python scripts/private_network.py --json
```

Then confirm Hermes services are bound to the same address with your OS socket/network tools and run:

```bash
python scripts/doctor.py --json --redact
```

If peer connectivity works but Hermes ports do not, inspect the NetBird source/destination groups and access policy before weakening the host firewall or changing Docker to `0.0.0.0`.

## Upstream references

- NetBird self-hosting: https://docs.netbird.io/selfhosted/selfhosted-quickstart
- Local users: https://docs.netbird.io/selfhosted/identity-providers/local
- Network access policies: https://docs.netbird.io/manage/access-control/manage-network-access
- Ports/firewalls: https://docs.netbird.io/about-netbird/ports-and-firewalls
