# Threat model

This project assumes the agent is powerful enough to read files, browse the web, execute commands and call external tools. Privacy therefore depends on **limiting authority and data flow**, not only on choosing open-source software.

## Assets to protect

Highest-sensitivity assets include:

- Codex/ChatGPT OAuth state and API credentials
- Hermes `.env`, `auth.json`, sessions and private `USER.md`/`MEMORY.md`
- Hindsight memories and knowledge graph
- browser cookies/session stores
- Google/GitHub/other OAuth refresh tokens inside integration services
- documents ingested into Docling/OpenViking/knowledge stores
- backup archives

## Primary threats

### 1. Accidental public service exposure

Mitigations:

- loopback bind by default,
- server mode rejects wildcard/global addresses,
- private/Tailscale IP only for shared services,
- Tailscale ACL guidance,
- OpenViking not auto-started before authenticated config exists.

### 2. Silent data exfiltration through fallback providers

Mitigations:

- Hermes `web.search_backend` explicitly set to SearXNG,
- `web.keyless_fallback: false`,
- `web.keyless_rescue: false`,
- optional cloud services are explicit rather than automatic.

### 3. Prompt injection through web pages/documents

A page, document or retrieved memory can contain instructions hostile to the user's intent.

Mitigations:

- treat retrieved content as data, not authority,
- separate read/research tools from high-authority write tools,
- require confirmation for destructive/external actions,
- keep credentials out of prompts/memory,
- use dedicated profiles/banks for higher-risk browsing when appropriate.

### 4. Malicious or compromised MCP/skill

MCP servers and skills can effectively extend the agent's authority.

Mitigations:

- reviewed catalog instead of auto-installing popular tools,
- minimal tool allowlists,
- high-authority integrations disabled by default,
- third-party skill hashing/review workflow tracked in ROADMAP,
- PR checklist requires privacy/supply-chain review.

### 5. Memory poisoning / stale personal model

Long-term memory can preserve incorrect, malicious or obsolete conclusions.

Mitigations:

- profile-isolated Hindsight banks,
- memory hygiene skill,
- explicit correction rather than blind duplication,
- future retention/mission policies per bank,
- backup before migrations.

### 6. Cloud backup disclosure

Mitigations:

- no live DB sync,
- logical exports,
- rclone crypt/restic/age before cloud storage,
- backup manifest hashes,
- restore drills.

### 7. Supply-chain compromise

The stack currently consumes several upstream container images and official installers.

Mitigations today:

- minimal components,
- CI syntax/secret checks,
- explicit image override variables,
- no auto-update of service images during normal stack repo update.

Planned before 1.0:

- pinned image versions/digests,
- SBOMs,
- vulnerability scanning,
- release provenance/signing.

## Out of scope / cannot guarantee

The stack cannot protect data if:

- the host OS/account is already compromised,
- a user deliberately gives an untrusted MCP broad filesystem/shell access,
- credentials are pasted into prompts or committed to Git,
- an authorized cloud provider itself receives data the user chose to send,
- an upstream model/provider retains data under its own policy.

Privacy-first means reducing unnecessary exposure and making trust boundaries visible; it does not turn a general-purpose agent into a formally isolated security system.
