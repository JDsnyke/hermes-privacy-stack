# Memory sync across multiple Hermes instances

## Recommended pattern

Run **one authoritative Hindsight server** and connect every Hermes instance to it over Tailscale/WireGuard.

Each client uses:

```json
{
  "mode": "local_external",
  "api_url": "http://<private-host>:8888",
  "bank_id": "hermes",
  "bank_id_template": "hermes-{profile}"
}
```

This produces banks such as `hermes-default`, `hermes-coder` and `hermes-researcher`. The same named profile on multiple devices therefore shares memory while different profiles remain isolated.

## Why not Drive/Syncthing for live memory?

Databases use locking, WAL files and multi-file transactional state. File-sync tools can copy a half-updated state and corrupt or fork it. Use the service API for live sharing.

## Backup/migration

Hindsight 0.8+ provides logical whole-bank export/import through `hindsight-admin export-bank` and `import-bank`. Exported archives omit embeddings and regenerate them at import, which is preferable to raw DB copies for portability.

Encrypt exports before uploading to Google Drive. Planned backends are restic and rclone crypt; see ROADMAP.
