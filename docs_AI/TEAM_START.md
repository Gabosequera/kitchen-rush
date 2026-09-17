# Team Start Plan

This is the recommended first round for four learners.

The goal is parallel work with real dependencies, not four isolated mini-projects.

## Learner A — Menu Foundations

Primary file: `kitchen_rush/menu.py`

Focus:

- `normalize_item_name`
- `get_menu_item`
- `calculate_item_price`

Run:

```bash
python checker.py --stage 1
```

Concepts: functions, strings, return values, conditions, types.

## Learner B — Orders

Primary file: `kitchen_rush/orders.py`

Focus on the MVP functions only. Leave locked post-MVP capabilities alone.

Run:

```bash
python checker.py --stage 2
```

Concepts: dictionaries, lists, mutation, loops, state.

## Learner C — Inventory

Primary file: `kitchen_rush/inventory.py`

Focus on the two MVP inventory functions. Do not implement reservations yet.

Run:

```bash
python checker.py --stage 3
```

Concepts: iteration, validation, boundaries, atomic mutation.

## Learner D — Kitchen Integration

Primary file: `kitchen_rush/kitchen.py`

This role intentionally depends on contracts implemented by the other learners.
Read `docs_AI/CONTRACTS.md` instead of rewriting their modules.

Run:

```bash
python checker.py --stage 4
```

Concepts: imports, integration, shared state, function composition.

## First merge checkpoint

After the four branches are ready:

1. review each other's pull requests;
2. merge one branch at a time;
3. run the full checker after every merge;
4. fix regressions without rewriting unrelated student code;
5. when the MVP passes, run Shift 1 together.

## Rotation rule

After the first merge checkpoint, rotate ownership.

Example:

```text
Round 1
A -> menu
B -> orders
C -> inventory
D -> kitchen

Round 2
A -> kitchen
B -> inventory
C -> orders
D -> menu / integration review
```

The exact rotation can change. The important rule is that nobody permanently owns one module.

## Do not work ahead by default

Post-MVP TODOs already exist in the repository, but they are intentionally locked.
Let Shift Mode create the need for those capabilities unless the team explicitly decides to explore ahead.
