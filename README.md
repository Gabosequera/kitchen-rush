# Kitchen Rush

Kitchen Rush is a collaborative Python learning project for a team of four beginners.

You are not solving disconnected exercises. You are building a restaurant engine that will eventually be stressed by a deterministic shift simulator.

## The two phases

### Phase 1 — Build the restaurant MVP

The restaurant must be able to:

- load and search menu items;
- create and edit orders;
- calculate totals;
- validate and consume inventory;
- queue, prepare, and complete orders.

Run the checker whenever you want feedback:

```bash
python checker.py
```

The checker validates behavior and contracts. It does not require one specific implementation.

### Phase 2 — Survive the shifts

After the MVP passes:

```bash
python simulation/shift.py --shift 1
```

The simulator uses the system you built. Later shifts expose integration bugs, higher traffic, new business requirements, and performance problems.

Every simulation is reproducible with a seed and reports a day, simulated time, order ID, and event ID when something fails.

## Team workflow

Work through GitHub issues. Prefer one primary owner per file for small tasks, then rotate ownership between missions so everyone reads code written by other people.

Recommended branch names:

```text
feature/menu-search
feature/order-total
fix/inventory-consistency
refactor/order-book
```

Do not treat merge conflicts as failure. Some conflicts are intentionally useful learning moments.

Read `docs_AI/GIT_WORKFLOW.md` and `docs_AI/PROJECT_INTENT.md` before making structural changes.

## Important rule about AI

AI may explain behavior, review diffs, run tools, and leave limited hints. It must not silently rewrite student-owned code or solve TODOs unless a human explicitly asks it to do so.

See `docs_AI/AI_RULES.md`.

## Useful commands

```bash
python checker.py
python checker.py --json
python simulation/shift.py --status
python simulation/shift.py --shift 1
python simulation/shift.py --shift 1 --seed 18472
python simulation/shift.py --reset-progress
```

## Python version

Python 3.11+ is recommended. The project uses only the standard library.
