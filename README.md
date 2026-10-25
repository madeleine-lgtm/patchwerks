---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# patchWERKS

One organization metarepo coordinates independent product repositories through GitHub Issues, the existing private Project, pinned revisions and Agentile. This repository contains governance and configuration; product code stays with its owner.

| Area | Existing or planned components | Model |
|---|---|---|
| Furb-o-Mek | Robot/streamer, website, Blinko Bot, speech integration | Preserve the existing furbomek product monorepo; keep reusable products separate |
| semanticore | GitGov, Exocore and future host/harness integrations | Shared product area with independent source and private host-state boundaries |
| Shared | jabberwerk, engineering contracts and adapters | Independent reusable components, pinned by consumers |

There is one coordination repo, not two competing product metarepos. A product may have its own monorepo and release train without becoming another organization control plane. The parent development folder remains an ordinary directory of sibling Git/jj checkouts.

Start at [AGENTS.md](AGENTS.md). Work from [the private delivery Project](https://github.com/orgs/patchwerks/projects/1). Existing Furb-o-Mek tasks and physical gates are preserved. [workspace.lock.json](workspace.lock.json) records the inspected integration revisions, not proof that those revisions are deployable together.

## Operating documents

- [Repository and authority model](docs/model.md)
- [Untrusted-contribution and execution boundary](docs/trust.md)
- [Project and harness adapter contract](docs/orchestration.md)
- [Git/jj contribution workflow](docs/jj.md)
- [Independent releases and integration pins](docs/releases.md)
- [Current rollout evidence and remaining gates](docs/rollout.md)

The foundation is configured separately from the remaining runtime integrations. No unattended reviewer, merger, deployment worker or automatic board synchronization is claimed merely because these files exist.

## Verification

Run `bash scripts/verify.sh` for this repository's metadata and Agentile gates. CI runs the same command on disposable GitHub-hosted runners with read-only repository access and no configured application secrets. Product acceptance remains in the product repositories.

## Upstream

Agentile foundations and ratchet scripts are adapted from [CitrateNetwork/agentile](https://github.com/CitrateNetwork/agentile/tree/4ea348d3babc7535bccb72fca8c6db53fc4c7feb). See [NOTICE](NOTICE.md) and the actual upstream Apache-2.0 [LICENSE](LICENSE). The upstream README's MIT statement conflicts with that license file; this adoption preserves the license file and does not treat the README statement as permission to relicense.
