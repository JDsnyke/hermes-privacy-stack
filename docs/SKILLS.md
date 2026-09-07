# Skills

Bundled local skills live under `skills/`. They are plain reviewed instructions and are safe to inspect before use.

Community skills are catalogued but **not auto-installed**. A skill can alter how the agent uses shell, browser, GitHub, memory or MCPs, so popularity/star count is not a security review.

## Review checklist

- exact source repository and commit/tag
- license
- network destinations
- shell/filesystem commands
- requested secrets
- destructive actions
- prompt-injection resistance
- whether it duplicates Hermes native functionality

The roadmap includes a staged installer that will download a skill to a quarantine/review directory, show the diff/hash, then enable it only after confirmation.
