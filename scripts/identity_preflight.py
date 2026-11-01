#!/usr/bin/env python3
"""Offline scope preflight; plans a token request, never mints or authorizes it."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import selectors
import stat
import subprocess
import time

POLICY_PATH = "policy/scoped-identities.json"
LIMIT = 65536
SHA = r"[0-9a-f]{40}"
PERMISSIONS = {
    "dispatcher": {"organization_projects": "write", "issues": "write", "pull_requests": "read", "metadata": "read"},
    "publisher": {"contents": "write", "pull_requests": "write", "metadata": "read"},
    "reviewer": {"contents": "read", "pull_requests": "write", "checks": "read", "actions": "read", "metadata": "read"},
}
OPERATIONS = {"publish_pr": "publisher", "review_pr": "reviewer", "project_update": "dispatcher"}
SCOPES = {
    "publish_pr": {"contents": "write", "pull_requests": "write", "metadata": "read"},
    "review_pr": PERMISSIONS["reviewer"],
    "project_update": {"organization_projects": "write", "metadata": "read"},
}
STATUSES = ("Backlog", "Ready", "In progress", "Review", "Blocked")
PROTECTED = (".git", ".github", ".agentile", ".agents", ".gitmodules", ".gitattributes",
             "policy", "config", "scripts", "tests", "manifests",
             "agents.md", "claude.md", "gemini.md", "hermes.md",
             "docs/trust.md", "docs/orchestration.md", "docs/releases.md",
             "docs/scoped-identities.md", "workspace.lock.json")


class Refused(Exception):
    """Only fixed public-safe messages are raised."""


def need(condition, reason="invalid schema"):
    if not condition:
        raise Refused(reason)


def keys(obj, expected):
    need(type(obj) is dict and set(obj) == set(expected))


def positive(value):
    need(type(value) is int and value > 0, "invalid identity")
    return value


def text(value, pattern):
    need(type(value) is str and re.fullmatch(pattern, value) is not None)
    return value


def ids(value):
    need(type(value) is list and 0 < len(value) <= 100)
    for item in value:
        positive(item)
    need(len(value) == len(set(value)), "duplicate identity")
    return value


def timestamp(value):
    text(value, r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        raise Refused("invalid timestamp") from None


def decode(raw):
    need(len(raw) <= LIMIT, "input exceeds limit")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refused("invalid JSON")))
    except (ValueError, UnicodeError, RecursionError):
        raise Refused("invalid JSON") from None


def read_json(path):
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as source:
            info = os.fstat(source.fileno())
            need(stat.S_ISREG(info.st_mode) and info.st_size <= LIMIT, "input file rejected")
            return decode(source.read(LIMIT + 1))
    except OSError:
        raise Refused("input unavailable") from None


def git_read(directory, args, limit):
    # The clone and Git executable/configuration are trusted operator infrastructure.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_NO_LAZY_FETCH="1",
               GIT_TERMINAL_PROMPT="0")
    command = ["git", "--no-replace-objects", "-C", str(directory), "cat-file", *args]
    try:
        with subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ)
                    result = bytearray()
                    deadline = time.monotonic() + 10
                    while True:
                        left = deadline - time.monotonic()
                        need(left > 0 and selector.select(left), "trusted policy unavailable")
                        chunk = os.read(process.stdout.fileno(), min(8192, limit + 1 - len(result)))
                        if not chunk:
                            break
                        result.extend(chunk)
                        need(len(result) <= limit, "trusted policy exceeds limit")
                    need(process.wait(timeout=max(0.01, deadline-time.monotonic())) == 0,
                         "trusted policy unavailable")
                    return bytes(result)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
    except (OSError, subprocess.TimeoutExpired):
        raise Refused("trusted policy unavailable") from None


def validate_policy(policy):
    keys(policy, ("schema_version", "repository_ids", "project_node_ids", "roles",
                  "max_evidence_age_seconds", "required_checks"))
    need(type(policy["schema_version"]) is int and policy["schema_version"] == 1)
    ids(policy["repository_ids"])
    projects = policy["project_node_ids"]
    need(type(projects) is list and 0 < len(projects) <= 20)
    for item in projects:
        text(item, r"[A-Za-z0-9_-]{1,128}")
    need(len(set(projects)) == len(projects))
    need(positive(policy["max_evidence_age_seconds"]) <= 300)
    keys(policy["roles"], PERMISSIONS)
    for role, identity in policy["roles"].items():
        keys(identity, ("app_id", "installation_id", "bot_user_id"))
        for value in identity.values():
            positive(value)
    for field in ("app_id", "installation_id", "bot_user_id"):
        need(len({identity[field] for identity in policy["roles"].values()}) == 3,
             "roles must use distinct identities")
    checks = policy["required_checks"]
    need(type(checks) is list and 0 < len(checks) <= 30)
    names = set()
    for check in checks:
        keys(check, ("name", "app_id"))
        text(check["name"], r"[A-Za-z0-9_ ./-]{1,100}")
        positive(check["app_id"])
        need(check["name"] not in names)
        names.add(check["name"])
    return policy


def load_policy(directory, revision):
    text(revision, SHA)
    need(git_read(directory, ["-t", revision], 32) == b"commit\n", "revision is not a commit")
    return validate_policy(decode(git_read(directory, ["blob", revision + ":" + POLICY_PATH], LIMIT)))


def plan(policy, revision, request, observation, now=None):
    """Validate caller observations; no observation is authenticated by this function."""
    p = validate_policy(policy)
    text(revision, SHA)
    now = now or dt.datetime.now(dt.timezone.utc)
    need(type(request) is dict and type(request.get("operation")) is str)
    operation = request["operation"]
    need(operation in OPERATIONS, "operation excluded")
    common = {"operation", "repository_id", "head_sha", "author_id", "publisher_id", "reviewer_id", "changed_paths"}
    keys(request, common | ({"project_node_id", "status"} if operation == "project_update" else set()))
    repository = positive(request["repository_id"])
    need(repository in p["repository_ids"], "repository not enrolled")
    text(request["head_sha"], SHA)
    principals = [positive(request[k]) for k in ("author_id", "publisher_id", "reviewer_id")]
    need(len(set(principals)) == 3, "self review or shared publishing principal")
    need(request["publisher_id"] == p["roles"]["publisher"]["bot_user_id"] and
         request["reviewer_id"] == p["roles"]["reviewer"]["bot_user_id"], "principal not enrolled")
    paths = request["changed_paths"]
    need(type(paths) is list and 0 < len(paths) <= 500)
    for path in paths:
        text(path, r"[^\x00-\x1f\\]{1,240}")
        need(not path.startswith("/") and all(part not in ("", ".", "..") for part in path.split("/")))
        need(not any(path.casefold() == prefix or path.casefold().startswith(prefix + "/")
                     for prefix in PROTECTED), "protected change excluded")
    if operation == "project_update":
        need(request["project_node_id"] in p["project_node_ids"], "project not enrolled")
        need(request["status"] in STATUSES, "terminal or unknown status excluded")
    keys(observation, ("observed_at", "repository_id", "head_sha", "author_id", "installations",
                       "token_metadata", "checks", "model_budget"))
    observed = timestamp(observation["observed_at"])
    need(0 <= (now-observed).total_seconds() <= p["max_evidence_age_seconds"], "stale observation")
    need(positive(observation["repository_id"]) == repository and
         text(observation["head_sha"], SHA) == request["head_sha"] and
         positive(observation["author_id"]) == request["author_id"], "observation identity mismatch")
    keys(observation["installations"], PERMISSIONS)
    for role, install in observation["installations"].items():
        keys(install, ("app_id", "installation_id", "bot_user_id", "suspended", "repository_ids", "permissions"))
        for field, expected in p["roles"][role].items():
            need(positive(install[field]) == expected, "installation mismatch")
        need(install["suspended"] is False, "installation suspended")
        need(set(ids(install["repository_ids"])) == set(p["repository_ids"]), "installation repository scope mismatch")
        need(install["permissions"] == PERMISSIONS[role], "installation permissions mismatch")
    role = OPERATIONS[operation]
    token = observation["token_metadata"]
    keys(token, ("app_id", "installation_id", "bot_user_id", "repository_ids", "permissions", "expires_at", "revoked"))
    for field, expected in p["roles"][role].items():
        need(positive(token[field]) == expected, "token identity mismatch")
    need(ids(token["repository_ids"]) == [repository], "token repository scope mismatch")
    need(token["permissions"] == SCOPES[operation], "token permissions mismatch")
    need(token["revoked"] is False, "token revoked")
    need(0 < (timestamp(token["expires_at"])-now).total_seconds() <= 3600, "token expiry rejected")
    checks = observation["checks"]
    need(type(checks) is list and len(checks) <= 30)
    budget = observation["model_budget"]
    keys(budget, ("approved", "remaining_calls", "expires_at"))
    need(type(budget["approved"]) is bool and type(budget["remaining_calls"]) is int and budget["remaining_calls"] >= 0)
    budget_expiry = timestamp(budget["expires_at"])
    seen = set()
    for check in checks:
        keys(check, ("name", "app_id", "head_sha", "conclusion", "completed_at"))
        text(check["name"], r"[A-Za-z0-9_ ./-]{1,100}")
        positive(check["app_id"])
        text(check["head_sha"], SHA)
        need(type(check["conclusion"]) is str)
        completed = timestamp(check["completed_at"])
        need(0 <= (now-completed).total_seconds() <= p["max_evidence_age_seconds"], "stale check")
        need(check["name"] not in seen, "ambiguous check")
        seen.add(check["name"])
    if operation == "review_pr":
        need(budget["approved"] is True and budget["remaining_calls"] > 0 and now < budget_expiry,
             "model budget unavailable")
        for required in p["required_checks"]:
            need(any(c["name"] == required["name"] and c["app_id"] == required["app_id"]
                     and c["head_sha"] == request["head_sha"] and c["conclusion"] == "success" for c in checks),
                 "required current-head check missing")
    return {"schema_version": 1, "preflight": "consistent-observations", "execution_authorized": False,
            "observation_authenticated": False, "policy_revision": revision, "role": role,
            "operation": operation, "repository_id": repository, "head_sha": request["head_sha"],
            "planned_method": "POST", "planned_path": "/app/installations/" + str(p["roles"][role]["installation_id"]) + "/access_tokens",
            "planned_body": {"repository_ids": [repository], "permissions": dict(SCOPES[operation])}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-dir", type=Path, required=True)
    parser.add_argument("--trusted-revision", required=True)
    parser.add_argument("--request-file", type=Path, required=True)
    parser.add_argument("--observation-file", type=Path, required=True)
    args = parser.parse_args()
    try:
        policy = load_policy(args.repository_dir, args.trusted_revision)
        result = plan(policy, args.trusted_revision, read_json(args.request_file), read_json(args.observation_file))
    except (Refused, TypeError, ValueError, KeyError, OverflowError) as error:
        reason = str(error) if isinstance(error, Refused) else "malformed input"
        print(json.dumps({"preflight": "refused", "execution_authorized": False, "reason": reason}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
