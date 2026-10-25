---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Project adapter contract

Reuse organization Project 1 and its existing six statuses. Issues remain the durable work records; harness boards are execution projections. Keep the Project private because it can aggregate private-source work. The public coordinator contains only shareable policy and public-safe task summaries.

| Status | Dispatch meaning |
|---|---|
| Backlog | Untrusted intake or insufficiently specified work |
| Ready | Specified, dependency-checked and admitted by trusted triage |
| In progress | One dispatcher-acknowledged session owns the work |
| Review | Candidate revision and evidence await independent acceptance |
| Blocked | Explicit dependency, authority, access or physical prerequisite |
| Done | Terminal disposition; delivered only with completed reason and accepted evidence |

Add product Area and Risk classification without changing existing card status. Preserve the existing All work, Software, Physical gates and Ready to claim views. Area/risk fields are routing hints; validate them against current trusted policy rather than trusting contributor-supplied classification.

## Minimal adapter behavior

1. Discover Project, field and option node IDs through the API; store IDs in operator-private configuration. Do not scrape rendered board text or rely on field names as immutable identifiers.
2. Map each task to repository ID + issue node ID + canonical URL. A Project item ID is only its placement. Preserve native issue dependencies, PR links, closure reason and the owning PLAN/WP reference.
3. Have one trusted dispatcher admit and acknowledge a claim. Include task ID, harness/session ID, scope, workspace, issue-numbered branch, checkpoint and claim ID. GitHub assignment/comments/Project fields do not implement atomic compare-and-swap, leases or fencing. An adapter without qualified concurrency control must serialize dispatch; it may not claim distributed exclusivity.
4. Reconcile before each write. Keep the source event/delivery ID, source revision/update time, origin and idempotency identity in the adapter's existing durable store. Ignore duplicate delivery, do not echo the adapter's own updates, and refetch after uncertain responses. GitHub API operations are not exactly-once transactions.
5. Treat the issue body and attachments as data. Do not execute them, put private payloads on a public issue, or allow board edits to widen permissions. Close only after accepted evidence and published change; cancelled/not-planned is not delivered.
6. Resume after crashes by reconciling GitHub and recorded effects. A stale worker loses write authority; an expired claim alone is not permission to overwrite another session or re-run an uncertain side effect.

The owner is building Hermes/OmO-native/possible Herdr adapters. This repo specifies their shared interface; it does not ship a competing queue, message bus or orchestration service. GitGov's current lock/transaction implementation is local and Git-oriented, not a qualified distributed jj scheduler. Extend it only through its own governed implementation work.

## Native GitHub automation

Keep item-closed and merged-PR workflows as projections of accepted provider events. The existing Auto-close issue workflow means moving a card to Done can close an issue; restrict Project write to trusted dispatchers and keep this effect explicit until that workflow is separately disabled. Never let an untrusted worker use Done to bypass review. One Free-tier auto-add rule cannot cover every repository; API reconciliation supplies the remaining ingress.

For credentials, prefer an organization GitHub App with Projects write, Issues write, Pull requests read and Metadata read for the enrolled repositories. Mint only the permissions needed for each operation. Separate review/publishing principals; keep installation private keys and broad operator credentials outside builders. Registering/installing an App, wiring a receiver and proving restart/concurrency behavior are separate acceptance work.
