"""Synthetic offline observations are not signed approval or live qualification."""
import contextlib
import copy
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("identity", Path(__file__).parents[1] / "scripts/identity_preflight.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
HEAD, REV = "a" * 40, "b" * 40
NOW = dt.datetime(2026, 10, 30, 12, tzinfo=dt.timezone.utc)


def fixture(operation="review_pr"):
    roles = {role: dict(app_id=n, installation_id=n+10, bot_user_id=n+20)
             for role, n in zip(v.PERMISSIONS, (1, 2, 3), strict=True)}
    p = dict(schema_version=1, repository_ids=[100], project_node_ids=["SYNTHETIC_PROJECT"], roles=roles,
             max_evidence_age_seconds=300, required_checks=[dict(name="test", app_id=99)])
    request = dict(operation=operation, repository_id=100, head_sha=HEAD, author_id=50,
                   publisher_id=22, reviewer_id=23, changed_paths=["src/main.py"])
    if operation == "project_update":
        request.update(project_node_id="SYNTHETIC_PROJECT", status="Review")
    installations = {role: dict(identity, suspended=False, repository_ids=[100], permissions=copy.deepcopy(v.PERMISSIONS[role]))
                     for role, identity in roles.items()}
    token = dict(roles[v.OPERATIONS[operation]], repository_ids=[100], permissions=copy.deepcopy(v.SCOPES[operation]),
                 expires_at="2026-10-30T12:30:00Z", revoked=False)
    obs = dict(observed_at="2026-10-30T11:59:00Z", repository_id=100, head_sha=HEAD, author_id=50,
               installations=installations, token_metadata=token,
               checks=[dict(name="test", app_id=99, head_sha=HEAD, conclusion="success", completed_at="2026-10-30T11:59:00Z")],
               model_budget=dict(approved=True, remaining_calls=1, expires_at="2026-10-30T12:05:00Z"))
    return p, request, obs


class IdentityTests(unittest.TestCase):
    def runplan(self, p, r, o):
        return v.plan(p, REV, r, o, NOW)

    def test_all_plans_remain_unauthorized(self):
        for operation in v.OPERATIONS:
            with self.subTest(operation=operation):
                result = self.runplan(*fixture(operation))
                self.assertIs(result["execution_authorized"], False)
                self.assertIs(result["observation_authenticated"], False)
                self.assertEqual(result["planned_body"]["repository_ids"], [100])
                self.assertEqual(result["planned_body"]["permissions"], v.SCOPES[operation])

    def test_unknown_fields_rejected_everywhere(self):
        for target in ("policy", "request", "observation", "token"):
            p, r, o = fixture()
            selected = {"policy": p, "request": r, "observation": o, "token": o["token_metadata"]}[target]
            selected["hostile"] = "never echoed"
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_no_actual_token_is_accepted(self):
        p, r, o = fixture()
        o["token_metadata"]["token"] = "secret-that-must-not-appear"
        with self.assertRaises(v.Refused) as failure:
            self.runplan(p, r, o)
        self.assertNotIn("secret", str(failure.exception))

    def test_duplicate_json_keys_and_nonfinite_rejected(self):
        for raw in ('{"app_id":1,"app_id":2}', '{"value":NaN}', '{"value":Infinity}'):
            with self.assertRaises(v.Refused):
                v.decode(raw)

    def test_bool_ids_rejected(self):
        for location in ("policy", "request", "token"):
            p, r, o = fixture()
            if location == "policy":
                p["roles"]["reviewer"]["app_id"] = True
            elif location == "request":
                r["repository_id"] = True
            else:
                o["token_metadata"]["installation_id"] = True
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_shared_role_identities_rejected(self):
        for field in ("app_id", "installation_id", "bot_user_id"):
            p, r, o = fixture()
            p["roles"]["reviewer"][field] = p["roles"]["publisher"][field]
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_self_review_rejected(self):
        p, r, o = fixture()
        r["author_id"] = r["reviewer_id"]
        with self.assertRaises(v.Refused):
            self.runplan(p, r, o)

    def test_wrong_repo_and_installation_rejected(self):
        for change in ("request", "token_repo", "installation", "scope"):
            p, r, o = fixture()
            if change == "request":
                r["repository_id"] = 999
            elif change == "token_repo":
                o["token_metadata"]["repository_ids"] = [999]
            elif change == "installation":
                o["token_metadata"]["installation_id"] = 999
            else:
                o["installations"]["publisher"]["repository_ids"] = [100, 999]
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_elevated_and_missing_permissions_rejected(self):
        for permission in ("administration", "workflows", "contents"):
            p, r, o = fixture()
            o["token_metadata"]["permissions"][permission] = "write"
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)
        p, r, o = fixture()
        del o["token_metadata"]["permissions"]["actions"]
        with self.assertRaises(v.Refused):
            self.runplan(p, r, o)

    def test_revoked_or_suspended_rejected(self):
        p, r, o = fixture()
        o["token_metadata"]["revoked"] = True
        with self.assertRaises(v.Refused):
            self.runplan(p, r, o)
        p, r, o = fixture()
        o["installations"]["reviewer"]["suspended"] = True
        with self.assertRaises(v.Refused):
            self.runplan(p, r, o)

    def test_expired_or_long_lived_token_rejected(self):
        for expiry in ("2026-10-30T12:00:00Z", "2026-10-30T13:00:01Z"):
            p, r, o = fixture()
            o["token_metadata"]["expires_at"] = expiry
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_stale_or_future_observation_rejected(self):
        for stamp in ("2026-10-30T11:54:59Z", "2026-10-30T12:00:01Z"):
            p, r, o = fixture()
            o["observed_at"] = stamp
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_review_requires_current_head_checks(self):
        for change in ("missing", "head", "failed", "app", "stale"):
            p, r, o = fixture()
            if change == "missing":
                o["checks"] = []
            else:
                key, value = {"head": ("head_sha", "c"*40), "failed": ("conclusion", "failure"),
                              "app": ("app_id", 98), "stale": ("completed_at", "2026-10-30T11:00:00Z")}[change]
                o["checks"][0][key] = value
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_budget_absent_or_exhausted_rejected(self):
        for key, value in (("approved", False), ("remaining_calls", 0), ("expires_at", "2026-10-30T12:00:00Z")):
            p, r, o = fixture()
            o["model_budget"][key] = value
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_project_done_or_wrong_project_rejected(self):
        for key, value in (("status", "Done"), ("project_node_id", "OTHER")):
            p, r, o = fixture("project_update")
            r[key] = value
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)

    def test_excluded_operations_and_protected_paths(self):
        for operation in ("merge", "deploy", "admin"):
            p, r, o = fixture()
            r["operation"] = operation
            with self.assertRaises(v.Refused):
                self.runplan(p, r, o)
        for path in (
            ".github/workflows/test.yml", "policy/trust.json", "AGENTS.md", "../escape", "docs/trust.md",
            ".agents/skills/ratchet-check/SKILL.md", "CLAUDE.md", "GEMINI.md", "HERMES.md",
            ".gitmodules", ".gitattributes", "tests/audit_immutability.sh",
            ".AGENTS/skills/ratchet-check/SKILL.md", "Claude.Md", "Gemini.Md", "Hermes.Md",
            ".GitModules", ".GitAttributes", "Tests/audit_immutability.sh",
            "src/../tests/audit_immutability.sh", "tests\\audit_immutability.sh",
        ):
            with self.subTest(path=path):
                p, r, o = fixture()
                r["changed_paths"] = [path]
                with self.assertRaises(v.Refused):
                    self.runplan(p, r, o)

    def test_input_bounds_and_symlinks(self):
        with self.assertRaises(v.Refused):
            v.decode(b" " * (v.LIMIT+1))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input"
            path.write_text('{}')
            link = Path(directory) / "link"
            link.symlink_to(path)
            with self.assertRaises(v.Refused):
                v.read_json(link)

    def test_exact_git_policy_and_no_head_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], stderr=subprocess.DEVNULL).decode().strip()
            git("init", "-q")
            git("config", "user.name", "Synthetic")
            git("config", "user.email", "synthetic@example.invalid")
            git("commit", "--allow-empty", "-qm", "missing policy")
            missing = git("rev-parse", "HEAD")
            p, _, _ = fixture()
            path = Path(directory) / v.POLICY_PATH
            path.parent.mkdir()
            path.write_text(json.dumps(p))
            git("add", ".")
            git("commit", "-qm", "synthetic policy only")
            accepted = git("rev-parse", "HEAD")
            path.write_text('{}')
            self.assertEqual(v.load_policy(directory, accepted), p)
            for revision in (missing, "HEAD", git("rev-parse", "HEAD^{tree}")):
                with self.assertRaises(v.Refused):
                    v.load_policy(directory, revision)
            git("replace", missing, accepted)
            with self.assertRaises(v.Refused):
                v.load_policy(directory, missing)

    def test_cli_missing_policy_never_reads_observations(self):
        argv = ["identity_preflight", "--repository-dir", "/unused", "--trusted-revision", REV,
                "--request-file", "/unused", "--observation-file", "/unused"]
        output = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.object(v, "load_policy", side_effect=v.Refused("trusted policy unavailable")), mock.patch.object(v, "read_json") as read:
            with contextlib.redirect_stdout(output):
                self.assertEqual(v.main(), 2)
        read.assert_not_called()
        self.assertFalse(json.loads(output.getvalue())["execution_authorized"])


if __name__ == "__main__":
    unittest.main()
