# GitHub Pages

The `site/` folder is deliberately safe to publish: no user data, service health calls, secrets, analytics, remote fonts, CDN JavaScript or runtime configuration are included.

## Deployment is opt-in

The Pages workflow is gated so a repository with Pages disabled does not fail on every push.

Two ways to enable it:

1. Run **Deploy privacy-safe site** manually from GitHub Actions. The workflow asks `actions/configure-pages` to enable Pages.
2. After Pages is configured, add repository variable:

```text
HPS_ENABLE_PAGES=true
```

Then changes under `site/` deploy automatically.

If the repository is private and your GitHub plan does not support Pages for private repositories, keep the stack repo private and mirror **only `site/`** to a tiny public Pages repository.

## Never publish

Do not copy any of these into the site build:

- generated `stack.env`
- `.env` / `auth.json`
- `USER.md` / `MEMORY.md`
- Hindsight exports
- doctor/support bundles containing private hostnames or tailnet addresses
- OAuth setup files
- Activepieces/OpenViking credentials

## Browser-local configurator

The current configurator runs entirely in the browser and does not transmit selections. Future functionality that imports local health/config data must remain explicit opt-in and process the data client-side only.
