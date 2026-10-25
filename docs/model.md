---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Repository model and ownership

Use one thin organization coordination repository. Furb-o-Mek and semanticore are product areas, not competing metarepos. Preserve furbomek's atomic firmware/protocol/media changes and jabberwerk's engine-neutral speech monorepo. Reusable components keep their own versions. Existing personally owned website, bot, GitGov and Exocore repositories are candidates for later enrollment; no transfer or visibility change is implied here.

The XO product specification informs semanticore's requirements: scoped standing authority, independent enforcement and observation, durable state, verified outcomes and recovery. It is a product spec, not an order to operate live computers. Private source projects and private host state remain separate. Hardware and public-stream qualification remain Furb-o-Mek responsibilities.

## Authority

| Artifact | Owns |
|---|---|
| Owning repository PLAN.md | Product architecture and roadmap |
| GitHub Issue and native dependencies | Task identity, acceptance, discussion and terminal disposition |
| Shared Project | Dispatch status, ownership views, area and risk metadata |
| Agentile sprint/WP | Planned scope and accepted evidence/history, linked to issues |
| workspace.lock.json | Exact inspected cross-repository revision set |
| Local harness queue | Execution subtasks and session details referencing the issue |
| Enforcement boundary | Actual authority; never inferred from prose or a board card |

Repository instructions are not automatically inherited from another repository or the organization's .github repository. Every enrolled repository needs a local AGENTS entrypoint pointing at the pinned coordination policy and its own Agentile adoption. Never fetch and execute mutable remote policy on startup.

## Free-tier boundaries

GitHub Free supports the public coordinator's branch protections and repository rulesets. Private organization repositories lack the corresponding enforced private-repository protections; personal Pro does not upgrade the organization. Keep private-source builders unprivileged and autonomous merging disabled until an independently enforced merge boundary is qualified, or the owner explicitly chooses an eligible paid plan. Do not make private code public as a workaround.

Organization-level Projects offer one built-in auto-add workflow on Free. Use it selectively; the owner's forthcoming adapters should add other repository issues by the Projects API. Repository GITHUB_TOKEN cannot access the organization Project. A separately scoped GitHub App or authorized operator credential is required; do not give that credential to untrusted test execution.

Sources: [plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans), [repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets), [auto-add limits](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically), [Projects authentication](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions).
