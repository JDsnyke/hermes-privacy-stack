# Private overlay networking

Hermes Privacy Stack does **not** depend on a specific VPN vendor. Multi-device mode needs only a trusted private overlay address that is reachable by approved devices and is not globally routable.

The installer therefore binds services to one exact private IP and rejects wildcard/global addresses. The overlay is a transport/security boundary around Hindsight, SearXNG, Docling and other services; it does not replace application authentication where that exists.

## Recommended choices

| Option | Control plane | Clients | Best fit | Trade-offs |
|---|---|---|---|---|
| **NetBird self-hosted** | Self-hosted | NetBird | Best privacy-first all-in-one choice | Requires a publicly reachable management server/domain for normal self-hosted deployments; management/signal/relay components are AGPLv3 |
| **Headscale + Tailscale clients** | Self-hosted | Tailscale clients | Lightweight personal/small-lab control plane | Narrower feature scope than Tailscale SaaS; Headscale server normally needs to be internet reachable for roaming clients |
| **Tailscale** | Managed by Tailscale | Tailscale | Easiest setup and excellent cross-platform UX | Coordination/control metadata is handled by a third party |
| **Netmaker** | Self-hosted | Netclient / WireGuard | More traditional WireGuard network/site-to-site needs | Heavier operational model; server generally expects public IP/domain |
| **Plain WireGuard** | None | WireGuard | Small fixed device set, minimum moving parts | Manual key/routing lifecycle, no automatic NAT traversal or identity policy |

Other projects can be used if they provide a stable private IP per host. The stack should not assume a particular `100.x` allocation range.

## Default recommendation

For the project's privacy-first goal:

1. **NetBird self-hosted** when you are comfortable operating a small public management/control endpoint and want a complete self-hosted dashboard, policies, SSO/local users and cross-platform clients.
2. **Headscale** when you want the Tailscale client experience with a self-hosted coordination server and a deliberately smaller personal/lab-oriented scope.
3. **Tailscale** when operational simplicity matters more than self-hosting the control plane.
4. **Plain WireGuard** for a few static machines where manual networking is acceptable.

NetBird's current self-hosted quickstart uses a Linux VM, Docker Compose, a public domain and publicly reachable TCP 80/443 plus UDP 3478. It now includes local user management, so an external IdP is optional. Do not place Hermes/Hindsight/SearXNG themselves on those public ports; only the overlay control plane should be public where required.

Headscale is an open-source implementation of the Tailscale control server aimed at a single tailnet for personal/small-organization use. Its clients are standard Tailscale clients pointed at the Headscale server.

## Server setup

First join the always-on Hermes server to your chosen overlay and find its **overlay IPv4 address**.

### NetBird

```bash
netbird status --ipv4
```

Current NetBird clients expose `--ipv4` specifically for scriptable retrieval of the peer's overlay IPv4 address.

### Tailscale / Headscale

```bash
tailscale ip -4
```

### Plain WireGuard / Netmaker

Use the private address assigned to the WireGuard/Netmaker interface.

Then bind the stack to that exact address:

```bash
./install.sh --role server --bind-address 100.100.20.30
```

The installer rejects `0.0.0.0`, `::` and globally routable addresses.

## Clients

Join clients to the same overlay and point Hermes at the server's overlay IP:

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.100.20.30:8888 \
  --searxng-url http://100.100.20.30:8088
```

The address can belong to NetBird, Tailscale, Headscale, Netmaker, plain WireGuard or another trusted overlay.

## Least privilege

A private overlay IP is **not** sufficient authorization by itself. Apply provider ACL/policy rules or host firewall rules so ordinary clients can reach only what they need.

| Port | Service | Typical policy |
|---:|---|---|
| 8888 | Hindsight API | Hermes client devices |
| 8088 | SearXNG | Hermes client devices if search is shared |
| 9999 | Hindsight UI | Admin devices only |
| 5001 | Docling | Only clients that require document processing |
| 8090 | Activepieces | Admin/operator devices only |

Prefer deny-by-default rules.

## Provider notes

### NetBird

Advantages for this stack:

- WireGuard-based encrypted overlay.
- Fully self-hostable control plane.
- Native Windows, macOS, Linux, Android, iOS and additional NAS/firewall platforms.
- Granular access policies.
- Built-in local user authentication; optional OIDC/SSO.
- Scriptable `netbird status --ipv4` and JSON status.

Privacy/operations caveats:

- The normal self-hosted quickstart requires an Internet-reachable Linux VM/domain for coordination/NAT traversal.
- Management, signal, relay and combined server components use AGPLv3; other repository portions remain BSD-3-Clause.
- Keep the public control plane separated from the private Hermes service host when practical.

### Headscale

Advantages:

- Self-hosted, open-source Tailscale control server.
- Standard Tailscale clients across platforms.
- Supports base networking, DNS, tags, routes/subnet routers/exit nodes and ACL/policy functionality.
- Particularly well suited to a personal/small network.

Caveat: it intentionally implements a narrower scope than Tailscale's managed service.

### Tailscale

Best UX and easiest first install. It remains a valid option, but is no longer the architectural default in project documentation. Treat it as one provider implementing the private-overlay interface.

### Netmaker

Useful when the desired topology looks more like managed WireGuard/site-to-site networking, routers and gateways. It can integrate ordinary WireGuard clients, but its server deployment is heavier than NetBird/Headscale for a small personal Hermes mesh.

### Plain WireGuard

The smallest trust surface and no coordination SaaS, but keys, addresses, NAT traversal and peer configuration are yours to manage. Excellent for fixed server-to-server links; less ergonomic for laptops and phones that roam.

## Design rule for Hermes Privacy Stack

Code should ask for or auto-detect an **overlay private address**, never require a particular network vendor. Provider-specific automation is convenience only.
