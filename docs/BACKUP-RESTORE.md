# Backup and restore

## Separate backup classes

1. **Auth/secrets** — use OS credential backup or a dedicated encrypted secret archive; never Git.
2. **Hermes authored config** — SOUL/config/skills can be versioned or packed with `scripts/backup.py`.
3. **Hindsight memory** — use logical bank export/import.
4. **Knowledge files** — Obsidian/docs may use Syncthing or encrypted cloud sync if they are ordinary files, not databases.
5. **Service state** — database volumes require service-specific backup procedures.

## Cloud copy

Google Drive is acceptable as an encrypted object transport. Encrypt first using restic, age or rclone crypt. Do not rely on Drive privacy alone for personal memory.

## Restore test

A backup that has never been restored is unverified. Restore a bank into a temporary Hindsight instance/bank and test several known recall queries before deleting old backups.
