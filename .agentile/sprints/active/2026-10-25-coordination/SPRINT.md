---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
sprint: PW-0
status: active
---
# PW-0 coordination bootstrap

## Goal and authority

Configure the smallest GitHub-native, Agentile-based metarepo foundation requested by the owner. Public governance repository approved in this conversation; private source and host data remain private. No hardware, live service lifecycle, trading, wallet or platform-account action is authorized by this sprint.

## Work packages

- PW-0.1: Inspect current organization, board, product plans, XO PRD and Agentile source. Acceptance: record current repository ownership/visibility, board identities and the Free-tier limitations.
- PW-0.2: Configure one public coordination repository with pinned Agentile foundations, real ratchet tests, isolated read-only CI and mandatory all-harness instructions. Acceptance: local checks, adversarial boundary tests and actual GitHub CI results, followed by enforced main-branch protection.
- PW-0.3: Extend the existing private Project with product/risk metadata while preserving all ten initial issues and their status. Acceptance: API readback verifies unchanged existing items and the new fields.
- PW-0.4: Publish concrete adapter, trust, release and jj contracts. Acceptance: sources cited, no unsupported production claims, remaining identity/runtime gates represented by bounded issues.
- PW-0.5: Add pinned governance entrypoints to the two current organization repositories through reviewable PRs, preserving existing plans and runtime restrictions. Acceptance: independent review and checks before merge; pending PRs remain explicitly pending.

## Verification choices

No new distributed scheduler, credential broker, execution daemon or state machine is implemented here, so TLA+ and Gherkin implementation steps are not applicable to PW-0. This is configuration/adoption work. Upstream Agentile's baseline and vacuity regression tests exercise the ratchet behavior. Adversarial checks must show that lowering a candidate baseline cannot override a trusted base and that absent evidence cannot yield a graduated pass.

## Evidence and remaining work

Append exact revisions and observed results during closeout. Product adapters, independent review identities and privileged/live execution are separate tracked work, not implied by this bootstrap.

## Changelog

- 2026-10-30: Prepared the PW-0.4 [issue 4](https://github.com/patchwerks/patchwerks/issues/4)
  offline [task-adapter conformance suite](../../../../docs/task-adapter-conformance.md).
  Tests model synthetic projection/reconciliation obligations only; no owner-native
  binding, privileged synchronization, persistence or concurrency qualification is
  delivered. Canonical acceptance and live task state remain on issue 4.
