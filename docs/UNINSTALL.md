# Uninstall

Decide first what you want to preserve. The stack separates repository code, Docker service data, Hermes user state and Hindsight memory.

## Before removal

For anything important:

```bash
python scripts/backup.py --mode full --bank hermes-default
```

Encrypt/move that backup before deleting the machine.

## Stop stack services but keep data

From the repository directory, use the generated runtime env file.

### macOS / Linux

```bash
docker compose \
  --env-file "$HOME/.hermes-privacy-stack-state/stack.env" \
  -f stack/compose.yml \
  --profile core \
  --profile automation \
  down
```

### Windows

The generated state is normally under `%LOCALAPPDATA%\hermes-privacy-stack`.

Stopping Compose does not delete named volumes unless `-v` is added.

## Delete service data permanently

Only after verified backups:

```bash
docker compose \
  --env-file "$HOME/.hermes-privacy-stack-state/stack.env" \
  -f stack/compose.yml \
  --profile core \
  --profile automation \
  down -v
```

This deletes local Hindsight, Ollama, SearXNG and Activepieces named volumes. It is irreversible without backups.

## Remove stack repository/runtime files

macOS/Linux defaults:

```bash
rm -rf "$HOME/.hermes-privacy-stack"
rm -rf "$HOME/.hermes-privacy-stack-state"
```

On Windows, remove the cloned repository and `%LOCALAPPDATA%\hermes-privacy-stack` only after confirming you no longer need generated runtime config/backups.

## Keep or uninstall Hermes separately

The stack does not own Hermes itself. To remove Hermes using its official uninstaller:

```bash
hermes uninstall
```

Hermes can offer to keep its configuration/state. If you plan to reinstall, preserving it may be useful.

## Remote/client machines

A client role has no local stack volumes. Removing its stack checkout does not delete the authoritative Hindsight bank on the server.
