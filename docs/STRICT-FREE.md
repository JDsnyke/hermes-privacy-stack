# Strict-free policy

Hermes Privacy Stack v2 uses a stricter definition than "open source" or "has a free community edition."

## Acceptance rule

A supported runtime service must be:

1. self-hostable on infrastructure you control,
2. usable indefinitely without a paid license key,
3. functionally complete for the role assigned to it in this stack,
4. free of paid feature unlocks for that role,
5. free of a mandatory commercial control plane,
6. usable without sending operational data to a vendor service,
7. replaceable/exportable without trapping user state in a proprietary hosted format.

Paid hosting, sponsorship, consulting or support does **not** automatically disqualify a project if the same software functionality remains available in the self-hosted release. Paid/Enterprise-only software capabilities do.

## Current supported set

| Role | Project | Why it passes |
|---|---|---|
| Agent | Hermes Agent | Self-hostable agent software; local/custom model endpoints supported |
| Local model server | llama.cpp | Local OpenAI-compatible inference server |
| Shared memory | mcp-memory-service | Self-hosted MCP + SQLite-vec, API-key auth |
| Search | SearXNG | Fully self-hosted metasearch |
| Documents | Docling / Docling Serve | Local parsing/conversion |
| Crawling | Crawl4AI | Local crawling/extraction without required SaaS |
| Browser MCP | Playwright MCP | Local browser automation |
| Automation | Node-RED | Self-hosted flows/APIs/credentials |
| Git | Forgejo | Fully self-hosted Git collaboration |
| Private networking | Headscale | Self-hosted coordination for compatible clients |
| Simple VPN | WireGuard / wg-easy | Self-hosted encrypted network |
| Reverse proxy | Caddy | Self-hosted TLS/reverse proxy |
| SSO/MFA | Authelia | Self-hosted authentication/authorization |
| File sync | Syncthing | Peer-to-peer self-hosted file synchronization |
| Backups | restic | Local encrypted deduplicated backups |
| Containers | Podman | Free/open container engine; Docker Engine compatibility is optional |

## Explicit exclusions

The repository previously experimented with several capable projects that no longer satisfy this stricter product rule for our assigned role. They are intentionally not supported profiles:

- Nango
- Activepieces
- Windmill
- Hindsight
- NetBird
- Firecrawl
- ToolHive
- OpenViking
- Ollama as the default model layer

This is not a claim that these projects are bad, insecure, or unusable for free. It means the project has chosen to avoid architectures where paid product tiers, Enterprise feature boundaries, or commercial control-plane capabilities can become part of the dependency story.

## External services are allowed only as optional clients

A user may still choose an external model or API. The clearest example is **ChatGPT/Codex OAuth**.

That does not change the strict-free baseline because:

- the local stack works without it,
- no bundled service requires it,
- the user explicitly opts in,
- OAuth is handled by Hermes rather than this repository,
- local llama.cpp remains the default model path.

The same rule applies to an optional GitHub mirror: Forgejo can remain the canonical self-hosted Git service while GitHub is an optional external copy.

## Review checklist for new dependencies

Before adding a service, answer all of the following:

- What exact role does it play?
- Can that complete role run locally without a license/payment?
- Are relevant auth, backup, multi-user, policy, API or integration features paid-only?
- Does self-hosting require a vendor control plane?
- Can the stack operate if the vendor disappears?
- Is the data format exportable?
- Can networking be restricted to loopback/private interfaces?
- Can credentials live outside Git?
- Is a smaller existing component already able to do the job?

If any functional requirement depends on a paid unlock, the service does not enter the supported stack.

## CI enforcement

CI validates the reviewed Compose image set and rejects known removed container families. `scripts/image_lock.py` also fails when an unreviewed image appears in Compose, forcing a deliberate supply-chain and strict-free review before release.
