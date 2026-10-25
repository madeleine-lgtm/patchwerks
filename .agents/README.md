# `.agents/skills/` — Agentile methodology as cross-harness skills

This directory packages the Agentile methodology's workflow commands as
[Agent Skills](https://agentskills.io/specification) in the cross-harness
`.agents/skills/` convention. Harnesses implementing this convention may discover
these skills. Other harness adapters must explicitly load the root AGENTS.md and
Agentile entrypoint; this repository does not claim automatic discovery by every engine.

## Why this exists

Upstream Agentile offers optional Claude Code slash commands (`/sprint`, `/journal`,
`/audit-drive`, etc.); those bindings are not installed in this adoption.
The skills in this directory are the **harness-agnostic** equivalent:
the same workflows, expressed as `SKILL.md` files that every compliant harness
can load.

## Skills

| Skill | Replaces (Claude command) | What it does |
|-------|---------------------------|--------------|
| [`audit-drive`](skills/audit-drive/SKILL.md) | `/audit-drive` | Author an audit, open a remediation sprint, or close findings |
| [`sprint`](skills/sprint/SKILL.md) | `/sprint` | Sprint lifecycle: kickoff, daily, close, status, index |
| [`journal`](skills/journal/SKILL.md) | `/journal` | Seed a Rule-12-frontmatter journal entry |
| [`case-study`](skills/case-study/SKILL.md) | `/case-study` | Seed a case study (anchor incident + generalizable lesson + enforcement surface) |
| [`essay`](skills/essay/SKILL.md) | `/essay` | Seed a historical-context essay (not governance) |
| [`ratchet-check`](skills/ratchet-check/SKILL.md) | `/ratchet-check` | Run the four ratchet checks (tests, specs, tripwires, frontmatter) |

## Relationship to `.claude/commands/`

The `.agents/skills/` files are the harness-agnostic invocation surface in this
adoption. Optional model-backed claim grading is intentionally excluded until its
provider access, budget and evidence semantics are configured; an unavailable grader
must never count as a successful review.

If a future sprint wants to deduplicate, the `.claude/commands/*.md` files could
be regenerated from the `SKILL.md` files (or vice versa). That is out of scope
for the sprint that created this directory.

## Progressive disclosure

Per the agentskills.io spec, only the `name` + `description` frontmatter
(~100 tokens per skill) loads at session start. The full `SKILL.md` body loads
only when the skill is activated. This keeps session-start cost minimal.

## See also

- [`../AGENTS.md`](../AGENTS.md) — project operating instructions.
- [`../.agentile/rules/CORE_RULES.md`](../.agentile/rules/CORE_RULES.md) — the 13 non-negotiable rules.
- [`../.agentile/AGENT_ENTRY.md`](../.agentile/AGENT_ENTRY.md) — the agent entry point.
- [Sprint file](https://github.com/CitrateNetwork/citrate-federation/blob/main/agentile/sprints/active/2026-08-11-agent-agnostic-skills-and-agents-md.md) — AGNOSTIC-01 (the work package that created this directory).
- [agentskills.io specification](https://agentskills.io/specification)
