# AI Rules

These instructions apply to any AI assistant, coding agent, scheduled reviewer, or automated repository worker operating on Kitchen Rush.

## Student code is protected

Files under `kitchen_rush/` and `app.py` are student-owned learning code.

Unless a human explicitly requests a direct implementation, do not:

- implement TODOs for students;
- rewrite a student function;
- silently fix bugs;
- rename student variables;
- change formatting across student code;
- refactor working beginner code into advanced code;
- change a public function signature;
- remove duplicated or inefficient code only because it looks suboptimal;
- reveal the exact location or solution of a deliberate hidden bug;
- introduce a dependency when the same learning goal can be achieved with the standard library.

## Allowed AI behavior

An AI may:

- explain a traceback or concept;
- run `checker.py` and currently unlocked shifts;
- summarize recent Git changes;
- identify an observable regression;
- create an issue describing reproduction steps;
- point to a subsystem after the first hint is insufficient;
- ask students to inspect an input, output, type, state transition, or invariant;
- review pull requests without writing the solution.

## Hint budget

Use progressive hints.

### Hint level 1

Describe observable behavior and a minimal reproduction.

### Hint level 2

Name the subsystem or contract involved.

### Hint level 3

Name the relevant state transition or data shape.

### Never by default

Provide the final implementation, corrected function body, or exact deliberate-bug line.

Escalate only after repeated student attempts or when a human explicitly requests stronger help.

## Tooling protection

`checker.py`, `simulation/`, and `docs_AI/` define the curriculum and game mechanics. Do not modify them during normal student assistance.

If a human explicitly asks to evolve the curriculum itself, tooling changes are allowed but must preserve backwards-compatible contracts unless the curriculum document is also updated.
