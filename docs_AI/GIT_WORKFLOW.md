# Git Workflow for Four Learners

## Basic rule

Prefer one primary owner for a small task, but rotate modules across later tasks.

No person should permanently own one subsystem.

## Suggested cycle

1. Pick or create a GitHub issue.
2. Pull `main`.
3. Create a focused branch.
4. Make small commits with meaningful messages.
5. Run `python checker.py`.
6. Run the highest currently available shift when the MVP is unlocked.
7. Push and open a pull request.
8. Another learner reads the code before merge.
9. Resolve conflicts together when they occur.

## Branch examples

```text
feature/menu-search
feature/add-order-item
fix/order-status
fix/inventory-atomicity
feature/order-cancellation
refactor/order-book
```

## Commit examples

Good:

```text
Implement menu item lookup
Fix exact-stock inventory check
Add order line validation
```

Less useful:

```text
stuff
changes
works now
```

## File ownership during a task

An issue may specify:

```text
Primary file: kitchen_rush/orders.py
Supporting files: none
Avoid editing: checker.py, simulation/
```

This reduces accidental conflicts while the team is learning.

Later integration issues may intentionally require touching code written by someone else.

## Merge conflicts

Do not immediately ask an AI to resolve every conflict. First identify what both branches were trying to preserve. Conflict resolution is part of the exercise.
