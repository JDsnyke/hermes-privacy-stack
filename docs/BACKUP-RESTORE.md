# Backup and restore

Hermes configuration, credentials, Hindsight memory and ordinary knowledge files have different backup requirements. Do not treat them as one directory-sync problem.

## 1. Sanitized config backup

Default mode excludes `.env`, OAuth/auth files, `USER.md`, `MEMORY.md`, sessions and live databases:

```bash
python scripts/backup.py
```

It creates a timestamped bundle containing a sanitized config archive and a SHA-256 manifest.

Use this for disaster-recovery scaffolding or reviewing configuration history. It is **not** a complete personal-agent backup.

Restore it only after reviewing overwrite conflicts:

```bash
python scripts/restore.py --safe-config /path/to/hermes-config-safe.tar.gz
```

Add `--force` only when you intentionally want to replace existing config files.

## 2. Full Hermes backup

Hermes' native backup is WAL-safe and includes credentials/authentication state. The stack delegates to it instead of copying SQLite files itself:

```bash
python scripts/backup.py --mode full
```

**Full backups contain secrets. Encrypt them before cloud upload.**

Restore through Hermes:

```bash
python scripts/restore.py --hermes-full /path/to/hermes-full.zip
```

Stop long-running gateways before major restores when practical and review Hermes' restore warnings before overwriting newer sessions.

## 3. Hindsight memory banks

Never copy the live `.pg0`/PostgreSQL volume to Google Drive or Syncthing.

Export one or more logical banks from the managed container:

```bash
python scripts/backup.py \
  --bank hermes-default \
  --bank hermes-coder
```

To include operational audit/LLM history:

```bash
python scripts/backup.py --bank hermes-default --include-history
```

Restore/import:

```bash
python scripts/restore.py \
  --hindsight-bank /path/to/hindsight-hermes-default.zip
```

Or import under a different bank id for a restore drill:

```bash
python scripts/restore.py \
  --hindsight-bank /path/to/hindsight-hermes-default.zip \
  --target-bank restore-test-2026
```

Hindsight whole-bank exports omit embeddings; the target regenerates them during import. A target bank must not already exist.

## 4. Encrypted cloud copy with rclone crypt

Google Drive, OneDrive and similar free storage can be useful as **object transport**, not as trusted plaintext memory storage.

Create an `rclone crypt` remote interactively with `rclone config`, backed by your chosen cloud remote. After you have verified that the destination really is a crypt remote:

```bash
python scripts/backup.py \
  --mode full \
  --bank hermes-default \
  --rclone-dest drivecrypt:hermes-backups \
  --confirm-rclone-crypt
```

The confirmation flag is intentional: the tool will not guess whether an arbitrary rclone destination encrypts filenames/content.

## 5. Ordinary knowledge files

Obsidian Markdown, exported documents and other ordinary non-database files may use Syncthing or encrypted cloud sync. Do not include OAuth tokens, browser cookie stores, `.env` files or service databases in those sync roots.

## Restore testing

A backup that has never been restored is unverified. Periodically:

1. export a Hindsight bank,
2. import it into a temporary bank/instance,
3. run several known recall queries,
4. compare expected facts and relationships,
5. delete the temporary bank after validation.

Keep at least one backup independent of the primary machine and one copy outside the primary physical location.
