---
created: 2026-10-29T19:07:42Z
branch: codex/5-hostile-audit-review
author: Codex
sprint: PW-0
status: active
---

# Hostile audit-helper inputs: local qualification candidate

This is a bounded PW-0.2 follow-up for [issue #5](https://github.com/patchwerks/patchwerks/issues/5),
based on accepted commit `b99937e5f22ff34455723aaca667b394bd2be86e`.
It tests the real `scripts/check-audit-diff.sh` entrypoint with temporary Git
repositories. It does not implement or qualify a dispatcher, artifact promoter,
issue interpreter, credential boundary or deployment executor.

## Enforcement map

| Input or boundary | Actual surface and evidence |
|---|---|
| Hostile repository path | Literal shell syntax/newline in the path argument; real helper permits a new correction and creates no command marker |
| Hostile audit filenames | Option-like, command-substitution, newline and tab names; NUL-delimited Git inventory confirms literal names, committed modifications are rejected |
| Candidate checker replacement | Candidate contains a replacement checker that would write a marker and return success; an explicit helper outside that candidate rejects deleted audit history, with no marker |
| Invalid baseline | Malformed/unknown/blob references reject; tests expose and fix acceptance of tree/tag objects |
| Issue/PR prompt injection | No issue-text execution surface exists here; not tested as an authority boundary |
| Forged receipts, stale review/head, promotion provenance | No executable validator/promoter exists here; not tested and not qualified |
| Dependency hooks, credentials, host/device/network isolation | Not exercised by this Git/helper test; the local outer worker restricts access, without certifying hosted CI |

## Reproduced defect and minimal fix

The accepted helper validates forty lowercase hexadecimal characters, then calls
`git diff`. Git also accepts tree IDs and annotated-tag object IDs there. With
unchanged audit contents, both returned success despite the exact-commit baseline
contract. The fix checks the object's actual type with `git cat-file -t` and
requires `commit` before diffing. It does not infer approval, ancestry or freshness
from a valid commit ID: the caller must still supply the correct trusted revision.

Accepted helper SHA-256:
`5c8e981ecefae239bad93e6f203575eb5374ecb39223d53ef6176452d1297abc`.
Initial type-check candidate helper SHA-256 (superseded below):
`a5cd7744509f62b8ada47dc92d50db00262768d459e36a3a52893c24690decd6`.

Observed locally: the eight new tests against the accepted helper produced six
passes and two failures (tree and tag). The candidate produced eight passes;
the existing baseline-reference test and four shell audit cases also passed.
The canonical `scripts/verify.sh`, using the accepted baseline reference, passed
with 13 tests versus the prior five, four tripwires and 29/29 frontmatter coverage.
Its empty formal-spec/production-source checks still report explicit vacuous
results; they do not acquire new coverage from this change. Shell syntax and
whitespace checks passed as well.
Empty arguments already reject with Bash status 1; malformed/unknown object
inputs use status 2. The suite preserves that distinction rather than treating
all rejection statuses as identical.

## Reproduction and worker limits

Run `python3 -m unittest discover -s tests -p test_hostile_audit_inputs.py -v`
inside a credential-free disposable worker. By default it tests this checkout's
helper. `AGENTILE_AUDIT_HELPER` can select an explicit absolute helper copied from
the accepted revision for the before/after comparison. The test driver chooses
this path; candidate fixture content does not. The accepted-helper bytes were
extracted using `git show` and kept outside every candidate fixture repository.

All fixture subprocesses receive an explicit minimal environment, no inherited
Git global/system configuration, no remotes and no credentials. Git templates,
hooks and commit signing are disabled in these disposable fixtures. Paths and
references are passed as argument arrays, never interpolated into shell commands.
Every Git/helper process has a ten-second timeout; output is captured. Fixture
data are fixed small strings and Git objects, with cleanup after each test.

Observed worker: Python 3.12.14 on macOS ARM64, empty outer environment, denied
network and private-home/device reads, read-only source, writes limited to a
private temporary fixture tree. No Docker socket, devices, real media, services
or production credentials were used. This is not a portable OS sandbox installer
or a claim that the helper enforces those resource restrictions itself.

## Remaining issue #5 gates

At the accepted revision, `.github/workflows/agentile.yml` selects a baseline but
still invokes the checked-out candidate's `scripts/verify.sh`. The explicit
trusted-helper invocation tested here is not wired into that workflow. Workflow
checker replacement, credential isolation and promotion remain unqualified and
unchanged by this patch. A green helper suite cannot accept issue #5, bootstrap
policy, an artifact receipt or a live deployment. No privileged runtime is added.

At the initial local checkpoint, this candidate was a branch/patch because the available repository identity
has read-only upstream access. Independent review and authorized publication are
separate gates. No permission expansion, upstream write, merge, fork or activation
is performed. Rollback removes the tests/report and reverts the small type check;
doing so restores the demonstrated tree/tag acceptance defect.

## Revalidation on 2026-10-30

The remote default branch still resolves to the accepted `b99937e` revision above.
This continuation preserves the existing six-line helper fix and adds two real
Git regressions: a rename with shell syntax/newline in its destination, and an
audit replaced by a symlink whose target contains the original text. Both reject
with `BLOCKER`; neither is accepted as a new correction.

The expanded ten-case hostile suite against the accepted helper produced eight
passes and the same two failures (tree and annotated-tag objects returned zero).
The candidate passed the canonical `scripts/verify.sh` with 15 total tests
(11 Python tests and four shell cases), four tripwires and 29/29 frontmatter.
The empty formal/production corpora remain explicitly vacuous. The run used a
disposable source copy with an empty environment, network and user-home/device
reads denied, and writes restricted to disposable scratch. Apple's Git launcher
reported denied xcrun cache writes; commands completed and the full gate exited
zero. This is local evidence, not Linux CI or independent approval.

At that checkpoint, the GitHub identity reported `pull: true`, `push: false` for
this public repository, and no upstream PR, board transition or issue closure was
claimed. The larger issue #5 isolation and promotion gates above remain open.

## Changelog

- 2026-10-30: Reproduced the accepted-helper defect, added rename/symlink cases,
  ran the expanded canonical gate and rechecked the publication-access blocker.

## Replacement-reference hardening on 2026-10-30

Two further real-Git fixtures reproduced a bypass in the initial type-check
candidate: a local replacement for the baseline hid an audit modification, and
a replacement for HEAD hid deletion. Both returned success before the fix.
This threat requires control of local repository metadata, for example a reused
checkout after candidate execution; ordinary committed PR files alone do not
install replacement refs. Fresh trusted checkouts remain necessary.

Both object-type admission and the audit diff now use `git --no-replace-objects`.
Git's [replacement documentation](https://git-scm.com/docs/git-replace) specifies
that replacement refs normally affect object reads and that this option disables
them. A third regression verifies that a tree replaced by a commit is rejected
at the object-type boundary. Previously that case failed later during diff;
it was not a third successful bypass.

The final candidate helper SHA-256 is
`9fdc3d5eb9000f0221cc9b0cd5a7b76e4ad0cc3675382caeba164f8274701f0e`.
The complete canonical gate passed with 18 tests (14 Python and four shell),
four tripwires and 29/29 frontmatter. Python 3.14.7 and Apple Git 2.39.5 were
used in the same empty-environment, network-denied disposable worker; selecting
the developer-tools Git executable directly removed the earlier launcher cache
diagnostics. Source was read-only and only fixture scratch was writable. No
dependency download, live resource or privileged worker credential was used.

This remains a local check of the helper, not enforcement of the whole CI trust
boundary. HEAD is still supplied by the caller's checkout; a trusted dispatcher
must pin and revalidate the candidate revision and reject concurrent mutation.
The helper does not make a malicious Git executable/configuration safe or attest
an artifact, review, production deployment or distributed claim.

Changelog continuation: 2026-10-30 adds three replacement-reference regressions
and the two-command hardening; the earlier 13- and 15-test counts are historical.

## Publication path

On 2026-10-30 the operator created the public contribution fork
[`madeleine-lgtm/patchwerks`](https://github.com/madeleine-lgtm/patchwerks).
The issue-numbered bookmark `codex/5-hostile-audit-review` is prepared for a draft
PR to `patchwerks/patchwerks:main` through that fork. This uses ordinary fork
contribution permissions; upstream write access is unchanged. No maintainer
approval, merge, board transition or broader issue acceptance is implied.
