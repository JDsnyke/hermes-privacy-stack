# Updating safely

Hermes Privacy Stack and Hermes Agent are separate update domains. Do not automatically update both unless you intend to.

## Check stack updates

```bash
python scripts/update.py --check
```

## Update the stack repository

```bash
python scripts/update.py
```

The updater:

1. refuses a dirty Git checkout,
2. records the current commit,
3. asks Hermes for a native quick backup when Hermes is installed,
4. runs static diagnostics,
5. performs a fast-forward-only pull,
6. runs bootstrap/privacy self-tests,
7. resets the repository to the old commit if validation fails.

It does **not** change running Docker services by default.

## Update service images too

```bash
python scripts/update.py --services
```

This pulls and recreates the core Compose profile after repository validation. Until stable releases pin every image, review upstream release notes before doing this on a high-value memory host.

Take a logical Hindsight bank export before major Hindsight upgrades:

```bash
python scripts/backup.py --bank hermes-default
```

## Update Hermes Agent too

Only when intended:

```bash
python scripts/update.py --hermes
```

The script delegates to:

```bash
hermes update --backup
```

so Hermes uses its own update planning, backup and service restart logic.

## Disable automatic repository rollback

For debugging only:

```bash
python scripts/update.py --no-rollback
```

The default rollback protects repository code/config only. It cannot undo migrations already performed by external service images; that is why service updates are a separate explicit flag.

## After every meaningful update

```bash
python scripts/doctor.py
hermes memory status
```

Then run a few representative Hindsight recall/reflect queries before trusting the updated system with new long-term work.
