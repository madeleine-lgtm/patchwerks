---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Releases and integration pins

Each product owns its release train. Preserve jabberwerk's current VERSION/VERSIONING.md authority, even where older architecture prose describes a different tag model. This coordinator's VERSION versions coordination contracts only; it never rewrites upstream package, protocol, firmware, model or product versions to match.

At a release boundary, accumulate the owning repo's accepted changes, classify compatibility using Semantic Versioning, run its actual acceptance suite, create the immutable annotated tag on the accepted commit, publish through the scoped release principal and verify the provider's tag/release/artifact identity. Do not bump every commit, move published tags or release from a dirty/floating branch.

Update workspace.lock.json through a reviewed integration PR with exact full commits. A release tag is human-readable metadata; full commits and artifact digests identify consumed bytes. Record contract versions, consumers, compatibility tests and migration/rollback in that PR. The initial lock records inspected source revisions and is not a deployment-approved bill of materials.

Multi-repository delivery is staged: compatible producer release, consumer PRs and checks, then the integration lock update. A breaking boundary needs an explicit migration; there is no atomic multi-repository commit. Pin Actions to full SHAs and external runtime artifacts to verified hashes/digests. Never put private voice data, model weights, wallet material or host snapshots into release assets.
