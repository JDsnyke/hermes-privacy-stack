# Services

## Core

### Hindsight
API `8888`, UI `9999`. Primary long-term memory. Keep private.

### Ollama
Container-network-only by default. Used for auxiliary Hindsight inference; not published to host.

### SearXNG
Host `127.0.0.1:8088`. Search backend. JSON format enabled for agent use.

### Docling
Host `127.0.0.1:5001`. Document parsing. Optional if resources are constrained.

## Optional

### Activepieces
Host `127.0.0.1:8090`. Stores sensitive OAuth/app connections. Personal single-container mode is convenient but not a scale-out topology.

### OpenViking
Host `127.0.0.1:1933`. Persistent knowledge/context. Requires model/config initialization before full use.

### Firecrawl
Not included in core Compose because current self-hosting is a multi-service stack and should follow the upstream versioned Compose. Install only when broad crawling materially improves your workflows.
