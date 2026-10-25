---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Untrusted contribution boundary

Issues, PRs, comments, filenames, dependency hooks, logs and review/model output are hostile-capable data. A label such as ready-for-agent is an intake signal, not an authority grant. Authorization comes from trusted policy and the authenticated actor at execution time. Fetch instructions and enforcement logic from the accepted base revision; proposed policy changes require independent review before use.

| Participant | Allowed capability | Excluded capability |
|---|---|---|
| External contributor | Submit Issues and fork PRs | Upstream write, credentials and production access |
| Builder/test worker | One disposable checkout, bounded CPU/time/network policy | Owner PAT, secret store, Docker socket, host home, private network, robot devices |
| Independent reviewer | Read exact PR/base SHA and evidence; publish review/check output | Change candidate code, publish releases, deploy or self-approve authored work |
| Trusted dispatcher/publisher | Validate a structured operation and write one allowed repo/issue/branch using a scoped credential | Execute candidate code, accept authority from issue text, administer the organization |
| Deployment executor | Promote an accepted immutable artifact to one approved target and verify health/rollback | Build arbitrary PR code with production secrets or deploy to unrelated targets |

Use GitHub-hosted disposable runners for untrusted CI. No self-hosted runner on the Omen, robot controller or privileged XO host accepts arbitrary public PRs. A container sharing host credentials/devices/socket is not the required boundary. Dependency installation and candidate tests are arbitrary code execution; a read-only token can still expose private source, so credentials must be absent from untrusted test processes.

Required checks alone are insufficient when the PR can change its checker. Protect .github, .agentile foundations, scripts/ci, policy, manifests and release configuration with code-owner and independent review. Revalidate the exact head SHA before merge; reject stale reviews/evidence after a push. Separate the PR author's publishing principal from the approving reviewer. Multiple model brands using the same GitHub author identity do not create independent approval.

Use pull_request for ordinary untrusted testing, read-only permissions, checkout persist-credentials:false, full action SHAs, timeouts and no interpolated issue/PR text in shell code. Do not combine pull_request_target or workflow_run credentials with checkout/execution of an untrusted head or downloaded candidate artifact. Artifact names and hashes are not authority; validate source workflow/repository, revision, schema and provenance before promotion.

Automation may autonomously accept routine work only after deterministic checks and an independent review are satisfied under a scoped standing grant. Governance, credential policy, workflows, wallet/finance, deployment authority, host security and physical safety changes remain outside that routine grant. They can be prepared autonomously but require the defined higher-authority acceptance. This does not require a human to approve every routine task; it prevents a model or hostile PR from expanding its own authority.

AI review tools are advisory until their real execution, output schema, account identity, data handling, budget and failure behavior are qualified. Subscription access is not evidence of an unattended API entitlement. In particular, GitHub Agentic Workflows documents API-key/OIDC authentication for Codex/Gemini engines, not automatic use of a ChatGPT or Google Business subscription. Its firewall/safe-output model is a candidate to reuse, not an already deployed patchWERKS service. Missing reviewers or provider access block the gate.

Sources: [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use), [GitHub Apps versus OAuth](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps), [Agentic Workflows authentication](https://github.github.com/gh-aw/reference/auth/).
