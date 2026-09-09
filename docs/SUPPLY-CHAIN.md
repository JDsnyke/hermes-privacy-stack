# Supply-chain hardening

Hermes Privacy Stack treats dependency pinning, SBOMs and vulnerability reports as release evidence. The normal local installer does **not** upload runtime state, memories, credentials, configuration databases or personal data for scanning.

## Current model

Development may evaluate mutable upstream tags such as `latest`, but a release candidate must first resolve every Compose image to an immutable OCI digest and preserve the resulting manifest as review evidence.

`python scripts/image_lock.py` is the source-of-truth helper for that process. It has an explicit audited list of every image variable used by `stack/compose.yml` and fails closed if Compose gains an image that the lock helper does not know about.

```bash
python scripts/image_lock.py --output-dir dist/supply-chain
```

It produces:

- `images.lock.env` — `HPS_*_IMAGE=repository@sha256:...` overrides suitable for reproducing the resolved image set on the same tested platform.
- `images.lock.json` — source refs, immutable digest refs, image IDs, platform metadata, repository and Git SHA.
- `SHA256SUMS` — hashes of the lock files.

The generated files are evidence, not secrets. They do not contain OAuth credentials, API keys, memories or user profile data.

## GitHub workflow

`.github/workflows/supply-chain.yml` runs the release-evidence pipeline. During hardening it also runs when its implementation or Compose image set changes; once stable, routine execution should be reduced to manual runs and release tags.

The workflow:

1. checks out the repository and configures Python using GitHub Actions pinned to full commit SHAs;
2. downloads exact Syft and Trivy release archives and validates hard-coded SHA-256 checksums before execution;
3. resolves all Compose image tags to immutable OCI digest references;
4. emits CycloneDX JSON and SPDX JSON SBOMs for the repository and each referenced container image;
5. scans the repository and each locked image with Trivy;
6. creates a vulnerability summary and hashes the complete evidence bundle;
7. uploads the bundle as a GitHub Actions artifact.

Current scanner pins:

| Tool | Version | Archive verification |
|---|---:|---|
| Syft | 1.51.1 | SHA-256 pinned from the immutable upstream GitHub release |
| Trivy | 0.74.0 | SHA-256 pinned from the immutable upstream GitHub release |

Do not replace checksum verification with `curl | sh` or a mutable scanner container tag in the release workflow.

## Vulnerability policy status

The first implementation is deliberately **evidence-only**: Trivy findings are recorded but do not yet fail a release solely by severity.

This is temporary. Before v1.0, the project needs a reviewed policy that distinguishes at least:

- critical/high vulnerabilities with a fixed version available;
- upstream findings with no available fix;
- false positives or vulnerabilities not reachable in the deployed configuration;
- accepted exceptions with owner, justification and expiry date;
- new findings relative to the previously approved release baseline.

The intended stable policy is that a new fixable Critical/High finding blocks release unless a documented, time-bounded exception is approved. Avoid a blanket allowlist that silently suppresses future CVEs with the same identifier or package family.

## Edge versus stable

`edge`/development may use mutable tags so upstream changes can be evaluated. Stable release material must instead carry a reviewed immutable image lock generated from the exact candidate commit.

A future stable-release flow should consume the approved lock rather than resolve `latest` at installation time. Multi-architecture releases also need platform-aware validation so an amd64-only resolution is not incorrectly treated as proof for ARM64.

## Provenance and attestation

The evidence bundle currently includes Git SHA metadata and complete SHA-256 hashes. Cryptographic release attestation/signing remains a P0 item.

GitHub-native artifact attestations can be useful where the repository/account plan supports them, but the stack should not make its core integrity model dependent on a paid GitHub plan. A portable signing path such as Sigstore/cosign or another verifiable signature mechanism should remain available for private repositories.

## Local verification

Pure parser tests require no Docker:

```bash
python scripts/image_lock.py --self-test
```

Full local lock generation requires Docker and network access to the configured registries:

```bash
python scripts/image_lock.py
sha256sum -c dist/supply-chain/SHA256SUMS
```

A generated digest lock is not by itself an endorsement of an image. Review its SBOM, vulnerability report, upstream release notes/license and runtime privileges before promoting it into the stable channel.
