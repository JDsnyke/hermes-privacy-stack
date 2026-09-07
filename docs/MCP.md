# MCP policy and catalog

MCP is an authority boundary. An MCP server is not harmless because it is local or open source.

## Risk classes

- **Low** — read/transform local data with narrow inputs and no external writes.
- **Medium** — reads broad local/private context or reaches external systems.
- **High** — can send email, change calendars/repos, execute shell/filesystem writes, manage credentials or create automations.

The machine-readable catalog is `catalog/mcps.json`.

## Defaults

No high-authority MCP is auto-enabled. Activepieces is installed only by explicit choice. Filesystem/GitHub MCPs are generally redundant with Hermes' native abilities; use them only when they provide a concrete benefit and restrict their tool surface.

## Activepieces

Use Activepieces as the Composio-style app integration gateway. It has a self-hosted MCP server and hundreds of app integrations. Configure app OAuth in its UI, then expose only selected flows/tools to Hermes.

## Tool selection rule

Prefer the least-authority path:

1. Hermes native read tool
2. read-only MCP
3. narrow write MCP
4. broad automation gateway

Never expose an entire SaaS account when the task only needs one reviewed action.
