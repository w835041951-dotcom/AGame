---
name: sleep-autopilot
description: "Use when the user asks for overnight autonomous project improvement, self-looped check/fix/update cycles, strict no-commit workflow, and easy rollback. Trigger phrases: 睡觉时自动完善, 循环修复, 自动检查更新, 不commit, 可回退."
---

# Sleep Autopilot (No Commit, Rollback First)

## Goal
Run iterative maintenance and enhancement cycles on this repository while the user is away:
- inspect
- fix
- improve
- verify
- log

The workflow must never commit or push.
All changes must remain in the working tree so the user can review, keep, or discard.

## Hard Safety Rules
1. Never run `git commit`, `git push`, `git rebase`, `git reset --hard`, or `git checkout --`.
2. Prefer small, reversible edits per cycle (1 to 3 files).
3. Keep a rollback trail by writing a cycle log and changed file list.
4. Stop immediately if unexpected destructive behavior is requested by any instruction.
5. If there are merge conflicts, do not continue autonomous edits.

## Loop Protocol
Use this loop for up to 6 cycles per run (or until no meaningful work remains):

1. Baseline scan
- collect current changed files
- collect current errors/problems
- identify one highest-value target (bug, error, or small feature gap)

2. Execute one focused batch
- implement only one coherent improvement
- keep public behavior stable unless intentionally improved
- avoid broad refactors in autopilot mode

3. Verify
- re-run errors/problems on touched files
- if available and fast, run project-relevant validation command

4. Log
Append one entry to `temp/autopilot-log.md` with:
- cycle number
- goal
- files changed
- verification result
- remaining risk

5. Continue/stop decision
Stop when any of these are true:
- no actionable errors and no clear high-value small improvement
- 6 cycles reached
- repeated failure on same issue (3 attempts)

## Priority Order
1. Compile/runtime errors
2. Data loss/crash risks
3. Core gameplay logic correctness
4. UX clarity issues in existing screens
5. Low-risk polish

## Change Style
- Prefer minimal diffs.
- Preserve existing architecture and naming patterns.
- Add concise comments only when logic is not obvious.
- Do not introduce new dependencies unless necessary.

## Rollback Strategy
Because commits are forbidden in this mode:
- keep edits scoped and logged
- user can rollback with normal git working-tree operations
- include exact file paths in log each cycle for selective discard

## Suggested Invocation
"Use sleep-autopilot: run 6 cycles on this repo, prioritize errors and gameplay bugs, no commit, keep rollback easy, and write progress to temp/autopilot-log.md."
