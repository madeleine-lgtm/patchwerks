#!/usr/bin/env bash
set -euo pipefail

repository="${1:?repository path required}"
baseline="${2:?trusted baseline SHA required}"
[[ "$baseline" =~ ^[0-9a-f]{40}$ ]] || exit 2

# git diff also accepts trees and annotated tags; neither is an exact commit ID.
if ! object_type="$(git -C "$repository" cat-file -t "$baseline" 2>/dev/null)" || [[ "$object_type" != commit ]]; then
  echo 'ERROR: trusted baseline must identify a commit object.' >&2
  exit 2
fi

if ! changes="$(git -C "$repository" diff --name-only --diff-filter=MDRT "$baseline" HEAD -- .agentile/audits/)"; then
  echo 'ERROR: audit history could not be verified.' >&2
  exit 2
fi
if [[ -n "$changes" ]]; then
  echo 'BLOCKER: existing audit records were modified, deleted, renamed or changed type.' >&2
  exit 1
fi
