# Memory sync across multiple Hermes instances

## Recommended pattern

Run **one authoritative Hindsight server** and connect every Hermes instance to it over Tailscale/WireGuard. Do not synchronize the Hindsight database directory itself.

Each client uses a provider config equivalent to:

```json
{
  "mode": "local_external",
  "api_url": "http://<private-host>:8888",
  "bank_id": "hermes",
  "bank_id_template": "hermes-{profile}"
}
```

This produces banks such as `hermes-default`, `hermes-coder` and `hermes-researcher`. The same named profile on multiple devices shares memory while different profiles remain isolated.

## Server setup

Prefer a Tailscale IP and bind Docker directly to that IP rather than `0.0.0.0`:

```bash
./install.sh --role server --bind-address 100.64.10.20
```

The installer rejects wildcard and globally routable addresses. A private bind is still not an authorization system: use Tailscale ACLs to restrict which devices/users can reach the memory host.

## Client setup

```bash
./install.sh \
  --role client \
  --hindsight-url http://100.64.10.20:8888 \
  --searxng-url http://100.64.10.20:8088
```

Hermes' Hindsight provider supports `local_external` plus `bank_id_template`. The stack uses `hermes-{profile}` by default.

## Why not Google Drive / Dropbox / Syncthing for live memory?

Databases use locking, WAL files and multi-file transactional state. File-sync tools can copy a half-updated state, fork two writers, or restore files out of order. Use the Hindsight service API for live sharing.

The same rule applies to Hermes SQLite/state databases: use Hermes' backup/import/profile-distribution features rather than live-syncing database files.

## What *can* be synchronized as ordinary files?

Good candidates include:

- Obsidian vaults and Markdown knowledge files
- reviewed skills/source code
- public-safe distribution config
- encrypted backup archives

Avoid syncing `.env`, OAuth state, live DB volumes, browser cookie stores or unencrypted memory archives through generic cloud folders.

## Backup/migration

Hindsight 0.8+ provides logical whole-bank export/import through `hindsight-admin export-bank` and `import-bank`. Exported archives omit embeddings and regenerate them at import.

The repository automates the local-container path:

```bash
python scripts/backup.py --bank hermes-default --bank hermes-coder
python scripts/restore.py --hindsight-bank path/to/hindsight-hermes-default.zip
```

For Google Drive/OneDrive/S3-compatible storage, configure an **rclone crypt** remote first, then explicitly confirm it when copying a backup:

```bash
python scripts/backup.py \
  --bank hermes-default \
  --rclone-dest drivecrypt:hermes-backups \
  --confirm-rclone-crypt
```

The script deliberately cannot infer that an arbitrary remote is encrypted.

## Conflict model

A profile bank is authoritative at the Hindsight server. Clients should not create separate same-named local banks and later try to merge them. If you intentionally experiment offline, use a different bank/profile name and migrate/curate facts deliberately instead of blind database merging.
