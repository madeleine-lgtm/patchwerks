---
created: 2026-10-30T11:36:40Z
branch: codex/3-scoped-identities
author: patchWERKS / Codex
sprint: PW-0
status: active
---
# Scoped identity preparation

This implements the offline preparation portion of [issue 3](https://github.com/patchwerks/patchwerks/issues/3), under PW-0.4 and its [bounded plan](../.agentile/sprints/active/2026-10-25-coordination/issue-3-plan.md). No App has been registered, installation selected, token minted, permission changed or live identity qualified by this change. `identity_preflight.py` checks schema and consistency of operator-supplied nonsecret observations and prints an installation-token request plan. Its output always says `execution_authorized: false` and `observation_authenticated: false`. It neither signs receipts nor invokes a network client or writer.

## Proposed roles

The JSON files under [config/github-apps](../config/github-apps) are explicit proposed permission plans, not GitHub registration manifests or deployed configuration. They intentionally contain no invented App, installation, bot or Project IDs and no credentials.

| Separate App | Registration permissions | Excluded capability |
|---|---|---|
| Dispatcher | Organization Projects write; Issues write; Pull requests read; Metadata read | Contents writes, review/publishing identity, administration |
| Publisher | Contents write; Pull requests write; Metadata read | Workflow permission, administration, independent approval |
| Reviewer | Contents read; Pull requests write; Checks read; Actions read; Metadata read | Contents writes, publishing identity, administration |

These are separate Apps with distinct App IDs, installation IDs and bot user IDs. Different model names sharing one bot do not meet independence. The publisher bot and the reviewer bot must also differ from the originating change author's identity. The `author_id` observation means the authenticated originating change author, not simply the PR creator when a publisher bot created the PR. Establishing that provenance is a future trusted collector's responsibility; a contributor assertion cannot establish it.

GitHub installation tokens can restrict repository IDs and permissions; permissions cannot exceed the App's grant. Token responses expire after one hour. The planner demands exact operation scopes, a single enrolled repository, nonrevocation, and positive remaining lifetime no greater than one hour. These metadata checks do not prove a token is valid. [GitHub installation token documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app).

Organization Projects permission cannot be narrowed to one Project through `repository_ids`. The dispatcher plan therefore retains broader organization-level Project capability even with one selected repository. A future writer must independently enforce the accepted Project node-ID allowlist on every operation. `project_update` permits only Backlog, Ready, In progress, Review or Blocked. Done is forbidden because the existing Project automation can close issues. No actual Project mutation is implemented.

## Exact policy selection

The caller must independently establish the accepted policy revision and run accepted verifier code from trusted infrastructure. The local clone, its Git metadata/configuration and Git executable must be operator-controlled. Candidate files, a candidate-selected commit, arbitrary JSON observations and a green preflight cannot establish acceptance.

```text
python3 scripts/identity_preflight.py \
  --repository-dir TRUSTED_LOCAL_CLONE \
  --trusted-revision ACCEPTED_FULL_COMMIT_SHA \
  --request-file NONSECRET_REQUEST_JSON \
  --observation-file NONSECRET_OBSERVATION_JSON
```

The fixed policy path is `policy/scoped-identities.json`. This change intentionally supplies no enrollment policy there. The loader requires a full lowercase 40-hex actual commit, disables replacement objects and lazy fetching, reads only that commit's blob, and never falls back to HEAD or the working tree. Git reads have ten-second and 64-KiB bounds. JSON files are regular non-symlink files with a 64-KiB read limit. Unknown fields, duplicate keys, malformed JSON, nonfinite constants and boolean IDs are refused. Exit 0 means consistent advisory planning only; exit 2 means refused/unavailable/malformed evidence. Diagnostics use fixed messages and never interpolate input values.

An accepted policy has exactly these fields:

- `schema_version`: integer 1.
- `repository_ids`: 1–100 distinct positive repository IDs.
- `project_node_ids`: 1–20 distinct nonempty GraphQL node-ID strings, at most 128 characters each.
- `roles`: exactly `dispatcher`, `publisher`, `reviewer`, each containing exactly positive nonboolean `app_id`, `installation_id`, `bot_user_id`. Each identity column must be distinct across all three roles.
- `max_evidence_age_seconds`: positive integer at most 300.
- `required_checks`: 1–30 entries, each containing a unique `name` and positive provider `app_id`.

No accepted identity or node IDs are invented in the repository. Collect real values during separately authorized enrollment; independently review and accept that policy before use.

## Request and observation contract

Every request contains exactly `operation`, `repository_id`, `head_sha`, `author_id`, `publisher_id`, `reviewer_id`, `changed_paths`. The three permitted operation values are `publish_pr`, `review_pr`, `project_update`. The latter additionally requires `project_node_id` and `status`; those fields are forbidden on other operations. All identity integers must be positive and nonboolean; head is a full lowercase SHA. The changed-path list is bounded, rejects traversal and known governance roots/files including `.github`, `.agentile`, `policy`, `config`, `scripts`, manifests and trust documents. This lexical guard cannot classify every security-sensitive change. A future writer still needs independently trusted scope classification and complete diff provenance; it cannot treat a caller's path list as authorization. Merge, deployment, administration and governance operations are not available.

Observations contain exactly:

- `observed_at`, `repository_id`, `head_sha`, `author_id`: UTC `YYYY-MM-DDTHH:MM:SSZ` freshness and identities matching the request.
- `installations`: the three role names, each with `app_id`, `installation_id`, `bot_user_id`, `suspended`, `repository_ids`, `permissions`. Identities must match policy; suspension must be false; selected repositories must equal the enrolled allowlist; granted permission maps must exactly equal the proposed role plans.
- `token_metadata`: `app_id`, `installation_id`, `bot_user_id`, `repository_ids`, `permissions`, `expires_at`, `revoked`. This is a deliberately nonsecret normalized projection, not a raw token endpoint response. Raw responses containing `token` are rejected. Metadata must match the selected role and single-repository operation scopes; revocation must be false. Actual token values must never enter files, arguments, logs or this program.
- `checks`: up to 30 objects containing `name`, `app_id`, `head_sha`, `conclusion`, `completed_at`. Names must be unique. Supplied checks must be fresh, and review requires every policy-required check to have the expected App ID, exact requested head and success conclusion.
- `model_budget`: `approved` boolean, nonnegative integer `remaining_calls`, and UTC `expires_at`. Review requires approval, positive calls and unexpired budget. This is caller-supplied metadata, not a billing integration or proof of subscription/API entitlement.

`publish_pr` plans Contents write, Pull requests write and Metadata read. `review_pr` plans the reviewer registration scopes. `project_update` plans only Organization Projects write and Metadata read, omitting the dispatcher's other registration permissions. The printed `planned_path` is the numeric `/app/installations/{installation_id}/access_tokens` endpoint and `planned_body` contains only `repository_ids` and `permissions`. The tool checks a proposed request against existing nonsecret token metadata as a rehearsal/revalidation exercise; it does not fetch initial token evidence or claim token issuance has occurred.

## Owner setup and acceptance runbook

1. Review the three proposed permission plans and the scope limitations above. Actual App registration and installation require owner access and trusted setup details that have not been supplied. The permission-plan flags describe nonoperational proposals; they do not encode or override the user’s authorization. Choose organization-controlled Apps and recovery ownership. Review actual endpoints against [GitHub's permission selection guidance](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app).
2. With the required owner access and trusted setup details available, register distinct Apps with exactly the reviewed grants. Install each only on selected repositories. Keep private keys and broad operator credentials in trusted secret infrastructure outside builders and candidate execution. Record verified numeric App, installation, bot and repository IDs from provider state. Discover Project node IDs through the authenticated provider API into operator-private configuration.
3. Independently review an enrollment policy commit and provision its full accepted SHA out of band. Verify no candidate can select policy, manipulate the trusted clone or replace the verifier. The public permission plans are not enrollment evidence.
4. In the trusted collector, project provider responses into this nonsecret observation schema, omitting actual tokens before persistence. Reconcile bot identity, installation suspension, repositories, grants and expiry. Establish originating author provenance, complete changed paths and exact head/check identities. Revalidate immediately before any separately authorized writer acts; stale snapshots and this planner's unsigned output are insufficient.
5. Exercise real token expiry and revocation, suspended installation, nonenrolled repository denial, surplus permission rejection, cross-role self-review rejection, changed-head/missing-check refusal and Project allowlist/Done refusal. Verify provider readback under the actual distinct principals. Register rollback/revocation ownership and retain public-safe evidence without tokens.
6. Qualify actual reviewer engine access, output schema, data handling, provider API entitlement, budget exhaustion and failure behavior. Subscription access and synthetic positive tests do not satisfy this gate. Keep independent review and protected-change acceptance mandatory.

Observed confined canonical verification: **24 tests passed, zero skips** (19 identity preflight tests and five existing baseline tests), four tripwires passed, and 30/30 frontmatter checks passed (previous baseline 29). Formal and production empty gates remain explicitly vacuous. Hosted CI has not yet been observed. Current acceptance state: offline implementation prepared and locally verified; these synthetic checks do not qualify live identities. Actual registration, installation, credential storage, minting, expiry/revocation, wrong-repository enforcement, authenticated author/reviewer separation, Project writer enforcement, model-budget integration and independent acceptance are all **Pending**. No live automation capability graduates from this work.
