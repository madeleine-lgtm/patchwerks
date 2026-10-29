---
created: 2026-10-29T20:18:35Z
branch: codex/issue-4-offline-contract
author: patchWERKS / Codex
sprint: PW-0
status: active
---
# Offline task-adapter contract preparation

Scope: [issue 4](https://github.com/patchwerks/patchwerks/issues/4), PW-0.4.
This is a synthetic conformance fixture suite and a pure reference decision model.
It is not a Hermes/OmO adapter, queue, dispatcher, durable store, GitHub client or
background service. Passing these examples does not establish real round trips,
crash safety, distributed exclusivity or exactly-once effects. Issue 4 remains open.

## Source and integration gap

The accepted coordinator base is `b99937e5f22ff34455723aaca667b394bd2be86e`;
GitHub's main revision was read back as the same revision during preparation.
The coordinator has no root PLAN.md, native adapter code or owner binding.
Its `docs/orchestration.md` explicitly delegates native implementations to the owner.
The inspected workspace's public Furbomek PLAN describes Hermes lifecycle/media
and A2A integration, which is not a Projects task-sync seam. No owner-provided
Hermes/OmO task adapter source or durable-store API was identified in the inspected
sources. This is a bounded source inventory, not a claim that no such code exists.

Required next inputs are each adapter's source revision and native task mapping,
its existing durable-store transaction boundary and receipt provenance mechanism,
and its trusted serialized-writer integration. Do not invent these APIs here.
Project field discovery, installation permissions and runtime qualification remain
separate owner work. No real Project IDs, credentials or host state appear here.

## Owner binding contract

`tests/task_adapter_contract/conformance.py` exports `assert_conformance(case,
evaluate)` for a Python unittest case and an owner-supplied normalized evaluator.
`evaluate(snapshot, delivery, recorded_effects)` returns a JSON-compatible decision
(`project`, `ignore`, `refetch` or `blocked`). The reference implementation lives
only under tests. These are fixture vocabulary, not a declared Hermes/OmO API.
An owner binding must translate real native observations and then pass these
vectors plus native persistence/transport/concurrency tests in its own repository.

`head` is one explicitly selected candidate revision, not a property of an issue.
Planning issues may use null with no PR/evidence and cannot be delivered. Multi-PR
acceptance aggregation is outside this bounded normalization and needs owner design.

The canonical snapshot supplies repository node ID, issue node ID and canonical
URL together. Project placement is never identity. Dependencies, PR links,
PLAN/WP, closure reason, head and evidence survive projection. Local subtasks do
not replace canonical data. `delivered` is only an observation of supplied closed,
completed, exact-head accepted/published evidence; it cannot close or approve an
issue. The fixture booleans do not validate evidence provenance or actor identity.

Only trusted provider receipt normalization may supply `confirmed_effect_id`;
it must correlate an emitted operation in the existing durable store. Never copy
this value from issue bodies or arbitrary origin fields. An origin string alone
cannot suppress a delivery. Real receipt authentication is not tested here.
Repository/node/URL consistency must be verified by the native provider fetch;
synthetic strings only check preservation and mismatch handling here.

Persist event/delivery identity, source revision, origin and effect outcome in the
adapter's existing durable store before relying on them across restarts. The suite
serializes/restores synthetic inputs; it does not implement or test disk durability.
An `unknown` effect for the same task always requires refetch, including with a
new delivery ID or a previously confirmed duplicate. The model never clears that
obligation. A native adapter must freshly reconcile provider state and recorded
effects before deciding what occurred; timeout, elapsed claim or restart is never
permission to repeat an uncertain write. This fixture has no retry-write decision.

All new write requests are blocked, even with injected serialized/claim flags.
Serialization is an external integration requirement, not a boolean qualification.
The suite supplies no fencing authority and proves no competing-writer exclusion.
A native writer needs independently demonstrated serialization and stale-worker
rejection before any privileged sync is enabled.

## Verification

Run `python3 -m unittest discover -s tests -v` inside a disposable, credential-free
worker with denied network, host-home and device access, bounded by a supervisor
timeout. The coordinator's existing `bash scripts/verify.sh` discovers these tests
through its unchanged ratchet command. The trusted baseline remains five tests;
synthetic vectors are subtests, not inflated independent test counts.
