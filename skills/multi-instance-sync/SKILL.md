# Multi-instance Sync

Treat Hindsight as a network service, not a file to sync. Use one authoritative server over a private tailnet. Configure all Hermes clients with the same `HINDSIGHT_API_URL` and `bank_id_template: hermes-{profile}`. Never synchronize live database files with Drive/Dropbox/Syncthing. Use logical exports for backup/migration.
