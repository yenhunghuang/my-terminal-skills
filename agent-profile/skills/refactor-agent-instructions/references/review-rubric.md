# Agent instruction review rubric

Use this rubric only after inventorying the workspace and verifying the current
tool's loading behavior. It supports judgment; it does not replace it.

## Contents

- Evidence record
- Retention score
- Placement questions
- Content-type defaults
- Migration patterns
- Final review

## Evidence record

For each disputed rule, note the strongest available evidence:

| Confidence | Evidence |
| --- | --- |
| High | current local code/tests, official loader docs, repeated observed failures |
| Medium | current project docs, one reproduced failure, official qualitative advice |
| Low | old comments, community anecdotes, search snippets, unverified benchmarks |

Keep high-confidence project constraints. Validate medium-confidence claims.
Do not make low-confidence size advice or model folklore a hard requirement.

## Retention score

Score each instruction independently. Use the result to prompt review rather
than mechanically deleting content.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Scope | rare corner | one subsystem | most tasks |
| Specificity | generic advice | local preference | surprising project invariant |
| Failure evidence | none | plausible/one case | repeated or reproduced |
| Omission impact | cosmetic | rework/CI failure | security, data, cost, architecture |
| Enforceability | formatter/test exists | partially enforceable | prose is necessary |

Subtract one point for each:

- duplicated authoritative content;
- volatile inventory, count, version, or model name;
- rationale longer than the rule;
- content already guaranteed by code, schema, test, formatter, or harness;
- advice a capable coding model follows without prompting.

Interpretation:

- **8–10:** keep near the affected work; root only if scope is broad.
- **5–7:** shorten or move to a nested rule.
- **2–4:** move to an on-demand reference or skill.
- **0–1:** delete unless a loader compatibility need justifies it.

## Placement questions

Ask in order:

1. Must the agent know this before its first repository action?
2. Does it apply to most files under the current instruction scope?
3. Is the rule difficult to infer from manifests, code, tests, or nearby style?
4. Has omission caused a real failure, or would failure be severe?
5. Can a deterministic mechanism enforce it instead?

Root placement normally requires yes to the first four and no to the fifth.
Path-specific content belongs beside the subtree. Long explanations and rare
procedures belong in references. Repeatable cross-project procedures belong in
Skills.

## Content-type defaults

| Content | Default treatment |
| --- | --- |
| Install/build/test commands | keep high in the nearest applicable entry |
| Runtime/language versions | keep if compatibility-sensitive; derive from manifest |
| Secret/destructive boundaries | keep concrete and pair with safe alternative |
| Non-obvious architecture invariant | keep concise; link detailed rationale |
| Directory inventory | reduce to responsibility map; remove counts |
| Style already enforced by tooling | link/run the tool; delete prose duplication |
| Framework tutorial | delete or link official/project docs |
| Rare recovery runbook | move to a reference |
| Tool-specific loader explanation | keep only in that tool's entry or adapter |
| Historical rationale | preserve in ADR/history unless needed to avoid recurrence |
| Model/tool micro-management | delete unless current traces show recurring failure |

## Migration patterns

### Monolith to entry plus reference

Keep commands, invariants, and routing in the entry. Move detailed architecture,
catalogs, tutorials, and failure case histories into one searchable reference.
Add descriptive links such as `Read Configuration when changing config loaders`;
do not merely link a file named `more.md`.

### Root to nested scope

Move UI rules beside the UI subtree, infrastructure rules beside deployment
code, and language-specific rules beside that package. Confirm the target tool
actually loads nested or path-scoped instructions before relying on this split.

### Prohibition to executable boundary

Rewrite `Do not instantiate HTTP clients` as `Use apiClient from <path>; direct
clients bypass retries and auth`. If enforceable, add a lint rule or test and
reduce the prose to the supported path.

### Duplicate copies

Choose a canonical source. Prefer generated/symlinked copies only when the tool
requires separate filenames and the repository already supports that mechanism.
Otherwise keep small tool-specific entry files that point to shared references.
After edits, compare required copies byte-for-byte.

### Stronger-model cleanup

Remove generic search, planning, formatting, and retry instructions first when
the new harness demonstrably supplies them. Remove domain constraints last.
Evaluate representative tasks and regressions rather than relying on model
marketing or context-window size.

## Final review

- Commands exist and use the repository's current package/tooling choices.
- Rules have clear scope and no parent/child contradiction.
- Every `do not` names the supported alternative.
- Examples are short, valid, and more useful than prose.
- Moved references retain working relative links.
- Always-loaded text contains no unnecessary current-state inventory.
- Generated, cached, vendored, and unrelated dirty files remain untouched.
- The handoff states evidence, assumptions, exclusions, and validation.
