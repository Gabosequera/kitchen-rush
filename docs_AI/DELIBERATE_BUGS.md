# Deliberate Bug Policy — AI / Maintainer Spoiler Notes

> SPOILER WARNING: Students should not use this document as a shortcut.

The starter code contains deliberate defects. Their purpose is to create different debugging experiences.

## Categories

### Visible contract bugs

These should be discoverable early by `checker.py`, such as incorrect types, malformed structures, or state not changing.

### Silent integration bugs

These may pass basic isolated checks but fail when modules interact under a specific shift scenario.

The primary early integration trap is shared ingredient accounting across multiple order lines. The simulator, not an obvious traceback, should make the inconsistency observable.

### Future dormant bugs

Some post-MVP starter code is deliberately inefficient or uses an unsuitable persistence format. These defects should remain irrelevant until the corresponding capability is unlocked.

## AI behavior around deliberate bugs

Do not create an issue that says "the bug is on line X" or provide a corrected implementation.

Prefer:

- a reproducible input;
- expected vs actual state;
- the invariant that was broken;
- at most the owning subsystem after the first hint.
