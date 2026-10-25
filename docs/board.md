---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Shared patchWERKS delivery

GitHub Issues are the canonical work records for Furb-o-Mek, semanticore and shared components. This private organization Project is the shared dispatch/status view. Hermes kanban, OmO-native and other harness queues retain the canonical issue URL and report evidence upstream; automatic cross-harness synchronization is not installed yet.

Use All work, Software, Physical gates, Ready to claim and the product-area views. Workflow: Backlog -> Ready -> In progress -> Review -> Done; unresolved prerequisites belong in Blocked. Area and Risk are routing hints, not authority grants. Check issue dependencies, current claims, owning PLAN and the Agentile WP before starting.

A claim records harness/session identity, issue-numbered branch/workspace, bounded scope, shared-resource ownership and next checkpoint. Assignment and card state are not atomic locks. Autonomous adapters must serialize through one trusted dispatcher until lease/fencing behavior has passed its own concurrency tests.

Acceptance requires exact-revision tests, independent review, published work and real-interface evidence. Moving a card to Done can trigger the existing Auto-close issue workflow; never use it to bypass review. Done is terminal disposition, not proof of delivery. Closed-as-not-planned work is not delivered work.

Physical tickets never authorize probing, reset, flashing, motion, public broadcasting or privileged host changes. Keep production/device execution separate from disposable PR testing. Private plans, transcripts, raw media and credentials stay outside public artifacts.

Current organization policy: https://github.com/patchwerks/patchwerks/blob/main/AGENTS.md
Adapter contract: https://github.com/patchwerks/patchwerks/blob/main/docs/orchestration.md
Furb-o-Mek product plan: https://github.com/patchwerks/furbomek/blob/main/PLAN.md

Release a claim with a checkpoint, evidence, remaining work and resource ownership. Return unfinished In progress work to Ready only when specified and unblocked; otherwise use Backlog or Blocked. The original ten Furb-o-Mek issues and their safety/dependency gates are retained.
