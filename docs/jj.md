---
created: 2026-10-25T13:54:14Z
branch: main
author: patchWERKS / Codex
status: active
---
# Git and Jujutsu interoperability

Keep each first-party repository as an ordinary Git-backed jj-compatible repository. Clone sibling repositories using their reviewed manifest URLs and revisions; do not use a superproject/submodule tree as the organization workspace. Preserve configured remote names in existing clones. Keep .jj ignored before taking snapshots.

The contribution sequence is: inspect task/base, create an isolated workspace, edit and describe the change, create an issue-numbered bookmark at that change, push it to the allowed head repository, then open a PR with explicit repository/base/head. Use jj for change manipulation and gh for GitHub operations. Do not use gh pr checkout as the jj update mechanism.

For a fresh clone, the native route is `jj git clone URL DESTINATION`; an existing clean Git clone can use `jj git init`. Do not convert another agent's live checkout as a side effect. Use separate jj workspaces or independent clones with scoped ownership, and recheck claims before editing shared files.

The publishing adapter must verify the remote head commit equals the intended jj commit and pass that exact SHA through review, checks and merge. jj change IDs are useful session identities but GitHub checks and PRs bind to commit SHAs. Rewriting a change requires fresh applicable review/evidence. Do not force-push shared main or change a published tag.

Git hooks are not enforced by jj. Run verification explicitly and enforce accepted checks through GitHub. Core jj does not support submodule working copies, Git LFS or partial clones according to its current compatibility page. jabberwerk's third-party submodules need explicit, independently tested Git-managed handling; preserving its root Git history is not proof that its full submodule tree is jj-native.

Annotated release tags may be created through Git on an explicitly accepted commit; do not confuse jj's lightweight-tag support with annotated tags. No custom VCS or replacement GitHub adapter is required.

Sources: [jj GitHub workflow](https://docs.jj-vcs.dev/latest/github/), [jj Git compatibility](https://docs.jj-vcs.dev/latest/git-compatibility/). Commands must be checked against the installed jj release; task verification uses the official v0.46.0 binary without a global installation.
