---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# patchWERKS coordination specification

The organization is a federated development workspace for Furb-o-Mek, semanticore and their shared components. Contributors describe outcomes, claim bounded work, build in isolated workspaces and publish verifiable changes through GitHub. Existing GitHub Issues, Projects, reviews, checks, releases and APIs provide the control surfaces; Agentile supplies the common engineering method.

The coordination repository owns project membership, exact integration pins, shared governance, adapter contracts and rollout records. Product code and canonical product plans stay in their owning repositories. Furb-o-Mek retains its product monorepo; jabberwerk retains its speech monorepo. semanticore contains the shared host/governance product area, including planned enrollment of GitGov and Exocore, without copying private machine state into public Git.

Autonomous operation means execution under previously established authority, independent checks and evidence. Untrusted Issues, PRs, comments, attachments, dependencies and model responses cannot change authority. Isolated builders, reviewers, publishers and deployment executors receive different capabilities. The implementation may be small, but those boundaries must remain explicit.

Acceptance requires real GitHub settings and Project state to match the checked-in configuration; required checks to fail for invalid changes; jj-to-GitHub contribution compatibility; preserved private content; Agentile entrypoints usable by every harness; and tracked, explicit prerequisites for any autonomous capability not yet deployed. A board, a green metadata check or an agent narrative is not proof of unattended production readiness.
