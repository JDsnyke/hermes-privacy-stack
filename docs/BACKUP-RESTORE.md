# Backup and restore

Hermes Privacy Stack v2 uses **restic** as the target encrypted backup backend. The migration is intentionally conservative: the current helper backs up Hermes artifacts safely but refuses to copy the live mcp-memory-service SQLite database until a consistency-safe automated procedure is tested.

## Threat model

Backups may contain more sensitive information than the repository itself:

- OAuth/API credentials in full Hermes backups,
- personal context and conversation state,
- semantic memories,
- Node-RED credentials/flows,
- private Forgejo repositories,
- service configuration and topology.

Treat backup encryption keys/passwords as high-value secrets.

## Sanitized Hermes config

```bash
python scripts/backup.py
```

This produces a local bundle containing only reviewed configuration/personality/skills material. It intentionally excludes `.env`, auth state, `USER.md`, sessions and service databases.

Restore:

```bash
python scripts/restore.py --safe-config /path/to/hermes-config-safe.tar.gz
```

Existing files are not overwritten unless `--force` is explicit.

## Full Hermes backup

```bash
python scripts/backup.py --mode full
```

This delegates to Hermes' native backup mechanism and may include OAuth/API credentials. Do not store the resulting ZIP unencrypted.

Restore:

```bash
python scripts/restore.py --hermes-full /path/to/hermes-full.zip
```

## restic

Configure restic using its normal environment or password-file/command mechanism. The stack backup helper deliberately does not accept repository passwords on the CLI.

Example environment:

```bash
export RESTIC_REPOSITORY=/mnt/backup/restic-hermes
export RESTIC_PASSWORD_FILE="$HOME/.config/restic/hermes-password"
```

Initialize once:

```bash
restic init
```

Create and snapshot a sanitized bundle:

```bash
python scripts/backup.py --restic
```

Full Hermes backup into restic:

```bash
python scripts/backup.py --mode full --restic
```

restic tags these snapshots with:

```text
hermes-privacy-stack
strict-free-v2
```

The repository may be local storage, NAS mount, SFTP or another restic-supported backend. No particular cloud provider is required.

## Shared semantic memory — current limitation

Do **not** run:

```bash
cp sqlite_vec.db ...
```

against a live memory service and assume the copy is consistent.

`backup.py --include-memory` currently refuses to run on purpose.

mcp-memory-service includes SQLite-oriented backup/export tooling upstream, and v2 will automate a tested service-safe path. Until that lands, perform memory backups only using the memory project's documented procedure or a deliberate stopped-service/cold-backup process that you have restore-tested.

The same rule applies on restore: `restore.py --memory-database` intentionally refuses to replace a live database.

## Future automated memory procedure

The acceptance path is:

```text
quiesce / service-safe SQLite backup
               ↓
verify backup integrity
               ↓
include in staging bundle
               ↓
restic snapshot
               ↓
restore into disposable instance
               ↓
known-memory search succeeds
```

Only then will memory backup be marked release-ready.

## Node-RED

Until the dedicated logical/cold-consistent helper lands, treat `/data` as service state rather than ordinary Syncthing content. Back it up only in a controlled snapshot/stop window or through a documented Node-RED export plus encrypted restic snapshot.

## Forgejo

Forgejo requires both repository data and its database/config to recover completely. Do not rely on copying only Git repositories if you need issues, users, keys, settings and metadata. A dedicated Forgejo backup path is tracked in the roadmap.

## Syncthing is not a backup database transport

Syncthing is appropriate for normal files such as:

- Obsidian vaults,
- documents,
- exported research notes,
- non-secret static config copies.

It is **not** the transport for live SQLite databases, auth/session directories or active service state.

## Recovery rule

A backup is not trusted until it has been restored and checked.

Keep at least one independent copy and schedule periodic recovery drills rather than relying only on snapshot success messages.
