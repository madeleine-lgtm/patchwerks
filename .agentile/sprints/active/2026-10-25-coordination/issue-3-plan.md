---
created: 2026-10-30T11:36:40Z
branch: codex/3-scoped-identities
author: patchWERKS / Codex
sprint: PW-0
status: active
---
# Issue 3 scoped identity preparation

This bounded PW-0.4 work package implements preparation for [issue 3](https://github.com/patchwerks/patchwerks/issues/3): explicit proposed permission plans for separate dispatcher, publisher and reviewer Apps; an offline, strict-schema installation-token request planner; and owner enrollment and qualification instructions.

The planner reads enrollment policy only from an independently accepted exact Git commit. No enrollment policy, credential, installation or live authorization is created by this work. Tests use synthetic policy commits and nonsecret observations. Passing preflight never authorizes execution. Actual registration, installation, token issuance/revocation, expiry enforcement, wrong-repository denial, independent review identity and model/provider budget qualification remain Pending.

Implementation scope is scripts/identity_preflight.py, tests/test_identity_preflight.py, docs/scoped-identities.md and config/github-apps/*.json. Supervisor owns confined execution and review. No worker network, candidate execution, commit, publication, account settings or permission changes are authorized.
