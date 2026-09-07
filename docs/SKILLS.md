# Skills

Hermes Privacy Stack treats skills as **executable agent policy**, not harmless prompt snippets. A skill can teach the agent to invoke shell commands, browsers, repositories, MCP tools, external services and helper scripts.

## Use Hermes' native security pipeline

Modern Hermes already provides a mature Skills Hub security path:

```bash
hermes skills browse
hermes skills search <query>
hermes skills inspect <identifier>
hermes skills install <identifier>
hermes skills audit
```

Hub installs are quarantined and scanned by Hermes for threats such as data exfiltration, prompt injection, destructive commands and supply-chain signals. A `dangerous` verdict cannot be overridden by `--force`; caution-level findings can be overridden upstream, but Hermes Privacy Stack deliberately avoids that path by default.

The stack therefore **does not maintain a competing home-grown security scanner**.

## Privacy-first wrapper

Use:

```bash
python scripts/review_skill.py <identifier>
```

to inspect without installing.

After source/license review:

```bash
python scripts/review_skill.py <identifier> --install
```

The wrapper enforces:

1. native `hermes skills inspect`
2. explicit acknowledgement of the exact identifier
3. native install-time quarantine/security scan
4. **no `--force` override**
5. native `hermes skills audit` after installation
6. a local non-secret review receipt stored outside Git

For a named profile:

```bash
python scripts/review_skill.py \
  skills-sh/obra/superpowers/verification-before-completion \
  --profile coder \
  --install
```

Audit a profile without installing anything:

```bash
python scripts/review_skill.py --profile coder --audit
```

Browse Nous Research's official optional skills first:

```bash
python scripts/review_skill.py --browse-official
```

Official optional skills should generally be preferred over community equivalents when they solve the same problem adequately.

## Bundled stack skills

The repository's locally reviewed skills live under `skills/`:

- `privacy-audit`
- `memory-hygiene`
- `document-intake`
- `research-pipeline`
- `multi-instance-sync`
- `backup-restore`

They are plain source-controlled instructions and can be audited directly in this repository.

## Curated community candidates

These are **candidates, not defaults**. Inspect current upstream content again before every install because repositories and hub metadata change.

| Hermes identifier | Purpose | Risk posture |
|---|---|---|
| `skills-sh/anthropics/skills/frontend-design` | High-quality frontend design guidance | Medium; generates/changes application code |
| `skills-sh/obra/superpowers/test-driven-development` | Test-first implementation discipline | Medium; influences coding workflow strongly |
| `skills-sh/obra/superpowers/verification-before-completion` | Require evidence before completion claims | Low/medium; useful guardrail for coder/operator |
| `skills-sh/obra/superpowers/systematic-debugging` | Structured debugging workflow | Medium |
| `skills-sh/vercel-labs/agent-browser/agent-browser` | Browser automation workflow | **High**; browser/session/network authority |
| `skills-sh/vercel-labs/skills/find-skills` | Discover additional community skills | **High**; expands supply-chain/discovery surface |

Do not install `find-skills` merely because it is popular. Hermes itself already has native `skills browse/search/inspect`, which is usually the safer and less redundant discovery path.

`agent-browser` is similarly optional: Hermes already has local browser capability. Add it only if its particular workflow/CLI materially improves a use case.

## Review checklist

Before approving a community skill, check:

- exact source repository/identifier and current upstream ownership
- license and redistribution constraints
- current Hermes/native security verdict
- scripts/binaries/packages it asks you to install
- network destinations
- filesystem scope
- requested environment variables/secrets
- destructive commands or external writes
- prompt-injection resistance and instructions that attempt to override higher-level policy
- whether it duplicates Hermes native functionality
- whether the selected profile genuinely needs it

Popularity, install count and GitHub stars are discovery signals—not a security review.

## Lean profiles

Hermes currently uses a deny-list model for enabled skills; installing/newly seeding skills can therefore broaden a profile unless explicitly disabled.

For a role that should start with the smallest possible skill surface, create it with:

```bash
python scripts/install_profiles.py researcher --lean
```

`--lean` uses Hermes' `--no-bundled-skills` profile creation option. Add only reviewed skills afterward.

For existing profiles, use Hermes' per-profile Skills UI/CLI to disable unnecessary skills. Do not rewrite an existing profile's skill policy automatically just because `--lean` was passed later.

## Agent-created skill writes

Hermes can gate agent-created skill modifications. For high-authority profiles, enable skill write approval through Hermes' supported `/skills approval`/configuration path so a model cannot silently persist a new procedural instruction without review.

Memory writes can be gated separately; see the memory/privacy documentation.

## Updating community skills

Do not auto-update high-authority skills unattended. Preferred flow:

```bash
hermes skills check
hermes skills inspect <identifier>
hermes skills update <name>
hermes skills audit
```

Review upstream changes before updating anything with browser, shell, deployment, secrets or repository-write authority.
