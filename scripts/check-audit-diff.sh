#!/usr/bin/env bash
set -euo pipefail

repository="${1:?repository path required}"
baseline="${2:?trusted baseline SHA required}"
[[ "$baseline" =~ ^[0-9a-f]{40}$ ]] || exit 2

if ! changes="$(git -C "$repository" diff --name-only --diff-filter=MDRT "$baseline" HEAD -- .agentile/audits/)"; then
  echo 'ERROR: audit history could not be verified.' >&2
  exit 2
fi
if [[ -n "$changes" ]]; then
  echo 'BLOCKER: existing audit records were modified, deleted, renamed or changed type.' >&2
  exit 1
fi
