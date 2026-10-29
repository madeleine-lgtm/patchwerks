"""Offline adversarial inputs against the real audit diff helper, not a dispatcher."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = Path(os.environ.get("AGENTILE_AUDIT_HELPER", ROOT / "scripts/check-audit-diff.sh")).resolve()
GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("git is required for real repository fixtures")


class HostileAuditInputs(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory(prefix="patchwerks-hostile-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        # Shell syntax remains literal data, including in the repository argument.
        self.repo = self.root / "candidate ; touch path-executed; #\n$(touch substituted)"
        self.repo.mkdir()
        home = self.root / "home"
        home.mkdir()
        self.env = {
            "PATH": str(Path(GIT).parent) + ":/usr/bin:/bin",
            "HOME": str(home),
            "TMPDIR": str(self.root),
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Offline fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Offline fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
        self.git("init", "--quiet", "--template=")
        self.audit = self.repo / ".agentile/audits/original.md"
        self.audit.parent.mkdir(parents=True)
        self.audit.write_text("original audit\n", encoding="utf-8")
        self.commit()
        self.baseline = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [GIT, "-c", "core.hooksPath=" + os.devnull, "-c", "commit.gpgSign=false", *args],
            cwd=self.repo, env=self.env, capture_output=True, text=True, check=True, timeout=10,
        )

    def commit(self) -> None:
        self.git("add", "--all", "--", ".")
        self.git("commit", "--quiet", "-m", "offline fixture")

    def gate(self, expected: int, baseline: str | None = None) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["/bin/bash", str(HELPER), str(self.repo), self.baseline if baseline is None else baseline],
            cwd=self.root, env=self.env, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        for directory in (self.root, self.repo):
            for marker in ("path-executed", "substituted", "filename-executed", "checker-executed", "ref-executed"):
                self.assertFalse((directory / marker).exists(), str(directory / marker))
        return result

    def test_real_helper_allows_new_correction_in_hostile_repository_path(self) -> None:
        self.audit.with_name("correction.md").write_text("new correction\n", encoding="utf-8")
        self.commit()
        self.gate(0)

    def test_hostile_audit_filenames_are_rejected_as_changes_without_execution(self) -> None:
        names = ("--output=filename-executed", "$(touch filename-executed).md", "line\nbreak.md", "tab\tname.md")
        for name in names:
            with self.subTest(name=name):
                path = self.audit.with_name(name)
                path.write_text("first version\n", encoding="utf-8")
                self.commit()
                baseline = self.git("rev-parse", "HEAD").stdout.strip()
                # NUL-delimited output verifies the literal name survived fixture setup.
                names_in_git = self.git("ls-files", "-z").stdout.split("\0")
                self.assertIn(str(path.relative_to(self.repo)), names_in_git)
                path.write_text("rewritten history\n", encoding="utf-8")
                self.commit()
                result = self.gate(1, baseline)
                self.assertIn("BLOCKER", result.stderr)

    def test_candidate_checker_replacement_cannot_change_explicit_trusted_invocation(self) -> None:
        replacement = self.repo / "scripts/check-audit-diff.sh"
        replacement.parent.mkdir()
        replacement.write_text("#!/bin/sh\ntouch checker-executed\nexit 0\n", encoding="utf-8")
        self.audit.unlink()
        self.commit()
        result = self.gate(1)
        self.assertIn("BLOCKER", result.stderr)

    def test_invalid_ref_text_never_becomes_shell_code(self) -> None:
        # Bash's required-argument check rejects an empty argument with status 1.
        self.gate(1, "")
        for ref in ("HEAD", "--output=ref-executed", "$(touch ref-executed)", self.baseline + "\n"):
            with self.subTest(ref=ref):
                self.gate(2, ref)

    def test_unknown_sha_fails_closed(self) -> None:
        self.gate(2, "1" * 40)

    def test_tree_object_is_not_a_trusted_commit(self) -> None:
        self.gate(2, self.git("rev-parse", "HEAD^{tree}").stdout.strip())

    def test_blob_object_is_not_a_trusted_commit(self) -> None:
        self.gate(2, self.git("rev-parse", "HEAD:.agentile/audits/original.md").stdout.strip())

    def test_tag_object_is_not_an_exact_commit_sha(self) -> None:
        self.git("-c", "tag.gpgSign=false", "tag", "-a", "fixture-tag", "-m", "offline tag")
        self.gate(2, self.git("rev-parse", "fixture-tag").stdout.strip())


if __name__ == "__main__":
    unittest.main()
