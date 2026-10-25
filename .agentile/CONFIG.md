---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Canonical coordination constants

- Organization: `patchwerks`, GitHub Free.
- Coordination repository: `patchwerks/patchwerks`, public governance and configuration only.
- Shared delivery Project: `https://github.com/orgs/patchwerks/projects/1`, private. Preserve its existing issues, access, views and statuses.
- Product areas: `Furb-o-Mek`, `semanticore`, `Shared`.
- Code layout: one organization metarepo over independent sibling repositories; product repositories may themselves be monorepos. Do not wrap sibling checkouts in a parent Git repository or new Git submodules.
- Agentile source: `CitrateNetwork/agentile` at `4ea348d3babc7535bccb72fca8c6db53fc4c7feb`.
- GitHub Issues own task identity, acceptance criteria, native dependencies and closure. The Project owns dispatch/status views. Repository `PLAN.md` files own architecture. Agentile sprint files own planned WPs and their acceptance/evidence history; they reference issue URLs instead of maintaining a second live task-status registry. This is the explicit patchWERKS adaptation of upstream Rule 9.
- Agentile ratchets apply to this coordination repository. They do not claim that downstream product CI, hardware tests or deployments pass.
- Private repositories keep their current visibility. Private source, XO PRD, credentials, host inventories, runtime logs and raw media stay outside this public repository.
- No unattended merger, release publisher, privileged host executor or board-sync daemon is installed merely by adopting this configuration. Those capabilities need their own scoped identities and acceptance evidence.

Before changing these constants, use a linked issue, reviewed migration and rollback record. The existing per-repository safety and ownership rules remain binding.
