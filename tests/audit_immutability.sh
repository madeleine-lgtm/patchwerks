#!/usr/bin/env bash
set -euo pipefail

project="$(cd "$(dirname "$0")/.." && pwd)"
suite="$(mktemp -d "${TMPDIR:-/tmp}/patchwerks-audit-tests.XXXXXX")"
trap 'rm -rf -- "$suite"' EXIT
passed=0

prepare_repository() {
  repository="$suite/$1"
  git init --quiet "$repository"
  git -C "$repository" config user.name 'patchWERKS test'
  git -C "$repository" config user.email 'test@example.invalid'
  mkdir -p "$repository/.agentile/audits"
  printf 'Original audit\n' > "$repository/.agentile/audits/original.md"
  git -C "$repository" add .agentile/audits/original.md
  git -C "$repository" commit --quiet -m 'Original audit'
  baseline="$(git -C "$repository" rev-parse HEAD)"
}

expect_result() {
  local expected="$1" actual=0
  bash "$project/scripts/check-audit-diff.sh" "$repository" "$baseline" > "$suite/result" 2>&1 || actual=$?
  if [[ "$actual" -ne "$expected" ]]; then
    echo "Audit gate returned $actual; expected $expected." >&2
    exit 1
  fi
  passed=$((passed + 1))
}

prepare_repository addition
printf 'Correction in a new audit\n' > "$repository/.agentile/audits/correction.md"
git -C "$repository" add .agentile/audits/correction.md
git -C "$repository" commit --quiet -m 'Add correction'
expect_result 0

prepare_repository modification
printf 'Rewritten audit\n' > "$repository/.agentile/audits/original.md"
git -C "$repository" add .agentile/audits/original.md
git -C "$repository" commit --quiet -m 'Rewrite original'
expect_result 1

prepare_repository deletion
git -C "$repository" rm --quiet .agentile/audits/original.md
git -C "$repository" commit --quiet -m 'Remove entire audit corpus'
[[ ! -d "$repository/.agentile/audits" ]] || exit 1
expect_result 1

prepare_repository invalid_baseline
baseline='1111111111111111111111111111111111111111'
expect_result 2

printf '%s\n' "$passed"
