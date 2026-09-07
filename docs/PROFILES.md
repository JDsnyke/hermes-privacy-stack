# Hermes profiles and starter personalities

Hermes Privacy Stack uses named Hermes profiles to separate roles, memory banks and tool authority instead of putting every workflow into one agent identity.

Hermes profile distributions preserve installer-owned memories, sessions, auth and `.env` across updates. `SOUL.md` is the durable identity/personality file; project-specific commands and repository rules belong in `AGENTS.md` rather than SOUL.

## Bundled profiles

| Bundle | Purpose | Suggested authority |
|---|---|---|
| `private-personal` | General personal assistant with conservative memory/tool behavior | Moderate; keep high-authority connectors opt-in |
| `coder` | Software engineering, architecture, testing and repository maintenance | Files/repositories/build tools; limit unrelated personal connectors |
| `researcher` | Evidence gathering, synthesis, source validation and dated research | Read-heavy web/doc tools; writes only to explicit research outputs |
| `operator` | Infrastructure, automation, backups and service maintenance | High authority; use only on trusted machines and narrow networks |

Because Hindsight uses `bank_id_template: hermes-{profile}`, these naturally map to separate long-term memory banks such as:

```text
hermes-private-personal
hermes-coder
hermes-researcher
hermes-operator
```

The same named profile on two machines can therefore share its bank while unrelated roles remain separated.

## Install starter profiles

List bundles:

```bash
python scripts/install_profiles.py --list
```

Install the recommended three:

```bash
python scripts/install_profiles.py private-personal coder researcher
```

Install every bundle:

```bash
python scripts/install_profiles.py all
```

Create shell aliases too:

```bash
python scripts/install_profiles.py all --alias
```

The installer uses `hermes profile create` **without clone/clone-all** so credentials, sessions and memory are not copied from another profile.

## Existing profiles are preserved

If a named profile already exists, the helper preserves its existing `SOUL.md` by default:

```text
↷ Preserving existing .../SOUL.md
```

Preview actions:

```bash
python scripts/install_profiles.py all --dry-run
```

Only replace an existing bundled SOUL deliberately:

```bash
python scripts/install_profiles.py coder --force-soul
```

Take a backup/export first if the existing profile matters.

## Interactive personality builder

`build_personality.py` creates a custom privacy-first `SOUL.md` from behavioral preferences rather than personal facts.

Interactive preview for the default profile:

```bash
python scripts/build_personality.py
```

Preview for an existing named profile:

```bash
python scripts/build_personality.py --profile coder
```

The builder asks only about:

- tone: neutral / warm / formal / direct
- verbosity: low / medium / high
- initiative: cautious / balanced / proactive
- confirmation threshold: strict / balanced / fast
- memory conservatism: minimal / balanced / rich

It shows a unified diff and is **preview-only by default**. Apply after reviewing:

```bash
python scripts/build_personality.py --profile coder --apply
```

For a deterministic non-interactive configuration:

```bash
python scripts/build_personality.py \
  --profile coder \
  --tone direct \
  --verbosity medium \
  --initiative proactive \
  --confirmation balanced \
  --memory balanced \
  --apply --yes
```

Before replacing a profile SOUL, the script copies the existing file into the local stack state directory under `personality-backups/<profile>/`. Those backups are runtime/user data and must not be committed to Git.

A misspelled/nonexistent named profile is rejected instead of silently creating an arbitrary profile directory. Create the profile first with `install_profiles.py` or Hermes' own profile command.

You can also generate a SOUL to a standalone file without touching Hermes:

```bash
python scripts/build_personality.py \
  --tone warm --verbosity medium --initiative balanced \
  --confirmation strict --memory minimal \
  --output ./SOUL-preview.md --apply --yes
```

This output mode is used by CI to ensure deterministic personality generation remains valid.

## Model / Codex OAuth

This repository never copies authentication between profiles. Configure model/auth through Hermes' own setup/model flow for each profile as required by the Hermes version you are running.

Examples:

```bash
hermes -p coder chat
hermes -p researcher chat
hermes profile use private-personal
```

## SOUL vs AGENTS vs USER

Use these boundaries:

- **SOUL.md** — who the agent is, tone, general behavioral priorities.
- **AGENTS.md** — project/repository-specific commands, architecture, workflow and operational instructions.
- **USER.md** — local user context the user deliberately wants available; never publish the populated file.
- **Hindsight** — learned durable facts/decisions/experience with profile-separated banks.

Keeping these roles distinct reduces prompt clutter and prevents repository-specific rules from contaminating unrelated work.

## Planned profile hardening

Next profile work should focus on **authority**, not more personality prose:

- profile-specific MCP allowlists
- profile-specific skill sets
- Hindsight mission/retention guidance by role
- an operator profile that requires stricter confirmation for destructive infrastructure changes
- documented rules for which connectors should never be shared across profiles
