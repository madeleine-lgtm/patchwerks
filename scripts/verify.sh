#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

jq -e '
  .schema_version == 1 and
  (.repositories | length > 0) and
  ([.repositories[].id] | length == (unique | length)) and
  all(.repositories[];
    (.repository | test("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")) and
    (.revision | test("^[0-9a-f]{40}$")) and
    (.visibility == "public" or .visibility == "private"))
' workspace.lock.json >/dev/null

python3 scripts/ci/check_test_ratchet.py --require-nonempty
python3 scripts/ci/check_spec_ratchet.py
python3 scripts/ci/check_tripwire_ratchet.py
python3 scripts/ci/check_frontmatter.py
python3 scripts/ci/check_no_mocks.py
python3 scripts/ci/check_no_unwraps.py
if [[ -n "${AGENTILE_BASELINE_REF:-}" ]]; then
  python3 scripts/ci/check_audit_immutability.py --since "$AGENTILE_BASELINE_REF"
else
  python3 scripts/ci/check_audit_immutability.py
fi

echo 'Coordination metadata and Agentile gates verified; downstream/runtime readiness is separate.'
