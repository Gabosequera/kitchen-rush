# Checker Design

`checker.py` is a curriculum-aware behavioral checker.

## Requirements

The checker must:

- survive missing modules and missing functions;
- catch import errors without crashing the whole report;
- validate behavior rather than source-code style;
- report received type and value when useful;
- show a small expected-structure example;
- skip dependent checks when prerequisites are missing;
- keep post-MVP stages locked until the simulator reveals them;
- expose machine-readable output through `--json` for an automated reviewer.

## What it must not do

The checker must not require a `for` loop, a specific variable name, a specific number of lines, or one exact implementation when multiple implementations satisfy the contract.

## Integration discoveries

Some checks intentionally become visible only after the simulator records a discovered integration problem. This preserves the difference between unit-level correctness and system-level behavior.
