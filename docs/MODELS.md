# Models

Model selection is deliberately separate from the service stack.

The strict-free stack does not require a commercial model provider. A user may nevertheless opt into ChatGPT/Codex OAuth when that is more useful than local inference.

## Option A — local llama.cpp (default)

Use an existing GGUF model:

```bash
./install.sh \
  --model-provider local \
  --llama-model /absolute/path/to/model.gguf
```

The bootstrap:

1. validates that the path is an existing `.gguf` file,
2. mounts only its containing directory read-only into the llama.cpp container,
3. starts the OpenAI-compatible llama.cpp server on the selected private bind address,
4. uses a 65,536-token context,
5. points Hermes at `http://<bind>:8080/v1`.

No model is silently downloaded by this repository. Model provenance, license and quantization should be reviewed before use.

### GPU layers

The Compose profile supports:

```text
HPS_LLAMA_GPU_LAYERS
```

The current default is `0` because portable GPU configuration differs across CUDA, Metal and CPU hosts. GPU-aware installation presets are tracked in `ROADMAP.md`.

### Context requirement

Hermes expects a model with at least a 64K context window. Do not assume that increasing llama.cpp's `--ctx-size` makes a model genuinely capable at that context; choose a model whose architecture/training supports it.

## Option B — optional ChatGPT / Codex OAuth

Interactive install:

```bash
./install.sh --model-provider chatgpt-oauth
```

The bootstrap invokes:

```bash
hermes model
```

Choose **OpenAI Codex / ChatGPT OAuth** in Hermes' own wizard.

Important boundaries:

- this repository never asks for your OAuth access/refresh token,
- tokens are not written into Git,
- OAuth is optional and does not affect the strict-free local service baseline,
- selecting it means prompts/model traffic are sent to the chosen external provider under that provider's terms,
- shared memory, private search and document services can remain self-hosted.

For non-interactive installation, the script cannot complete browser OAuth for you. It records the choice and instructs you to run `hermes model` locally afterward.

## Option C — configure later

```bash
./install.sh --model-provider skip
```

Then configure any Hermes-supported local/custom/provider endpoint later:

```bash
hermes model
```

## Multi-device recommendation

There is no requirement that every Hermes client use the same model provider.

For example:

```text
Desktop / GPU server       llama.cpp locally
Laptop                     ChatGPT/Codex OAuth
Travel machine             another local/custom endpoint
              \             |             /
               shared mcp-memory-service
               shared private SearXNG
```

That keeps durable context independent of the inference provider.

## Privacy recommendation

Use local llama.cpp for work where data should remain entirely on infrastructure you control. Use OAuth only when the benefits of the external model justify sending that request outside your self-hosted boundary.
