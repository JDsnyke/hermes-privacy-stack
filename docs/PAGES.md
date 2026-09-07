# GitHub Pages

The `site/` folder is safe to publish because it contains no user data, service health calls, secrets or analytics. It can be served from GitHub Pages by a small Actions workflow or mirrored to a public repository.

If the main repository is private and your GitHub plan does not support Pages for private repositories, keep the main repo private and mirror only `site/` to a public Pages repo. Never mirror generated runtime config.
