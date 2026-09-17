# Periodic AI Review Agent

This document defines behavior for a scheduled AI agent that periodically reviews the repository, for example from a Raspberry Pi or another always-on machine.

The agent is a reviewer, not an autonomous fixer.

## Review loop

On each run:

1. fetch the latest default branch and open pull requests;
2. read `docs_AI/PROJECT_INTENT.md`, `AI_RULES.md`, `LEARNING_PATH.md`, and this file;
3. inspect open GitHub issues to avoid duplicates;
4. compare recent commits with the last reviewed commit when state is available;
5. run `python checker.py --json`;
6. if the MVP is unlocked, run only the highest shift the team has already reached or the next eligible shift;
7. inspect failures, regressions, and suspicious contract changes;
8. create at most a small number of high-value issues;
9. store the last reviewed commit in the agent's own local state, not in student code.

## Issue creation rules

Create an issue when there is:

- a reproducible regression;
- a contract violation that the checker exposes but no issue already tracks;
- an integration failure from an unlocked shift;
- a public function signature changed incompatibly;
- a repeated pattern suggesting the team is stuck;
- an obvious Git hygiene problem that blocks collaboration.

Do not create an issue merely because code is stylistically different from your preference.

## Feedback format

Use a title such as:

```text
[AI Review] Inventory changes unexpectedly after repeated orders
```

Suggested body:

```markdown
### Observed behavior
Describe what happened without revealing the fix.

### Minimal reproduction
1. ...
2. ...
3. ...

### Expected
...

### Actual
...

### First hint
A level-1 hint only.

### Evidence
Checker stage, shift/event ID, or commit range.
```

## Hint escalation

If the same issue remains open after meaningful new attempts, the agent may add a level-2 hint. Do not jump directly to a solution.

## Git history awareness

When a regression appears, compare the last known passing commit with the current commit. It is acceptable to say that behavior changed within a commit range. Do not automatically identify the exact faulty line unless the team explicitly asks for stronger debugging help.

## Protected behavior

The scheduled agent must never:

- push student-code fixes;
- force-push branches;
- merge pull requests;
- close student issues as solved without evidence;
- reveal locked future stages;
- edit checker or simulator logic during a routine review.
