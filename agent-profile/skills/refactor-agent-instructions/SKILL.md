---
name: refactor-agent-instructions
description: Audit and simplify AGENTS.md and related agent instructions or skills when they are duplicated, stale, overprescriptive, or need recalibration for stronger models.
---

# Refactor Agent Instructions

Keep the smallest instruction set that changes useful behavior for a capable frontier model. Preserve user preferences and non-obvious project invariants; let the model infer ordinary engineering practice.

## Scope and evidence

- Locate applicable entry files and their owning repositories. Inspect Git status before editing; preserve unrelated changes. Back up originals when version history is unavailable.
- Edit first-party sources. Exclude caches, generated copies, and third-party packages unless explicitly in scope.
- Read each target fully. Verify commands, paths, and technical constraints against local code or tooling; consult current official documentation when a change depends on uncertain loader behavior or model capabilities.
- The optional [inventory script](scripts/inventory_instruction_files.rb) inventories agent instruction files. Supplement it with `rg --files --hidden` for `SKILL.md` and nonstandard filenames.

## Editing decisions

Retain concise preferences, commands that are hard to discover, domain invariants, and concrete operational boundaries. Remove duplicated policy, generic tutorials, volatile inventories, arbitrary line budgets, mandatory planning/delegation, and repeated verification unsupported by observed failures.

Preserve the user’s preferred model pool and provider routes. Default child work to the selected parent model; remove automatic cheap/fast routing without a task-specific reason. Do not infer capability from marketing suffixes. Name exact models only when they express an explicit preference or an operational requirement.

Put broad rules in the root entry, subtree rules near their scope, and useful conditional detail in linked references or skills. Do not move generic filler into references merely to shorten the entry. Adapt to the actual loader rather than forcing identical files on every tool.

Use [the review rubric](references/review-rubric.md) only for ambiguous retention or placement decisions. No scoring exercise is required for a straightforward edit.

## Validation

Check the diff for lost invariants and unintended edits. Verify changed links, referenced paths, frontmatter, and commands. Run `git diff --check` in changed repositories, or equivalent whitespace checks for unversioned files. Validate edited skills with the available skill validator.

Use behavioral tests only when the change affects a consequential workflow and a representative test adds confidence. Prose cleanup alone does not require a new worktree, benchmark, or multi-agent review.

Report the changed files, size changes, material policy changes, validation, and scope exclusions. Distinguish verified facts from assumptions.
