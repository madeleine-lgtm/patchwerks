---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
sprint: PW-0
status: active
---
# Coordinator quality floor

The initial behavioral test is the unmodified upstream regression proving that the trusted Git baseline wins over a PR-lowered candidate baseline. The upstream tripwire inventory counts four installed checks: frontmatter, audit immutability, no production mocks and no unwraps. The first two apply to this coordinator's documents; no-Rust checks and an absent audit corpus report their empty scope explicitly. Manifest revision validation is an additional executed metadata gate. These are not counts of product tests or evidence of runtime safety.

The test command in baseline.json propagates test failure with pipefail. The formal-spec baseline is intentionally empty for this configuration-only bootstrap and is visibly reported as VACUOUS, not claimed as formal verification. Future scheduler/authority state-machine changes require their own applicable proof/invariant tests.

Frontmatter coverage uses upstream's actual file inventory and is populated from measurement before publication. Ratchets read the accepted base revision in CI. Candidate changes to the workflow/checkers/policy still require independent code-owner review; counts and green checks are not a security boundary by themselves.
