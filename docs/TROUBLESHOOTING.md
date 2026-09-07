# Troubleshooting

Run:

```bash
python scripts/doctor.py
```

## Hermes missing after install

Open a new shell or reload your shell profile, then run `hermes --help`.

## Hindsight fails to start

```bash
docker compose -f stack/compose.yml --profile core logs hindsight
```

Embedded PostgreSQL can need more shared memory; the Compose file allocates `1gb`. Persistent-volume ownership can also matter on Linux.

## Local model unavailable

Check the Ollama container, then verify its model list. The stack pulls the default auxiliary model on first start; model compatibility may change, so see ROADMAP release checks.

## SearXNG not returning JSON

Confirm `stack/config/searxng/settings.yml` includes `json` under `search.formats` and restart the service.

## Client cannot reach server

Do not change loopback binds blindly. Confirm Tailscale/WireGuard connectivity and deliberately publish/proxy only the required service onto the private interface.
