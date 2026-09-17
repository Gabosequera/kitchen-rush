# Project Intent

Kitchen Rush is a collaborative learning codebase for four beginner programmers.

The project must feel like one real mechanism, not a worksheet containing unrelated exercises.

## Core learning goals

Students should repeatedly practice:

- reading code written by someone else;
- writing complete functions themselves;
- understanding input/output contracts;
- debugging behavior rather than matching one preferred implementation;
- integrating modules owned by different people;
- using Git branches, issues, commits, reviews, and merge conflict resolution;
- discovering why data structures and OOP become useful;
- distinguishing a bug from a new product requirement;
- profiling or measuring before optimizing.

## Two-phase design

### Phase 1: MVP

Students build the restaurant engine with functions, conditions, loops, lists, dictionaries, mutation, and module integration.

### Phase 2: Shift simulation

A deterministic simulator stresses the student implementation. Difficulty increases through higher volume, edge cases, cancellations, priority handling, indexed lookup, persistence, and final integration pressure.

The simulator is intentionally designed to expose specific classes of problems at specific points.

## Design principle

Do not remove an inefficient beginner solution simply because a more advanced solution exists. A later shift may be intentionally designed to make the limitation observable.

The learning sequence is:

1. make behavior correct;
2. integrate it with other code;
3. observe failure under real scenarios;
4. understand why the design fails;
5. improve the design for a reason.
