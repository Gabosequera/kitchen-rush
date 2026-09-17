# Shift Simulation Design

The simulator is deterministic and diagnostic.

## Reproducibility

Every run has a seed. Failure reports should include:

- shift number;
- simulated day;
- simulated clock time;
- event ID;
- order ID when relevant;
- seed;
- observed invariant or missing capability.

The same seed and shift must generate the same event sequence.

## Planned progression

### Shift 1 — Soft Opening

Small traffic. Confirms that the MVP works under normal use.

### Shift 2 — Shared Ingredient Trap

Introduces combinations where independently valid line items can exceed shared stock when considered together. Designed to expose an integration-level inventory bug.

### Shift 3 — Dinner Rush

More orders, repeated items, low stock, and state-transition pressure.

### Shift 4 — Change of Mind

Customers begin cancelling queued orders. This unlocks reservation/cancellation requirements rather than treating the missing capability as a bug.

### Shift 5 — VIP Night

Urgent orders and waiting pressure unlock priority selection.

### Shift 6 — Saturday Surge

Large order counts make linear lookup measurably expensive and unlock `OrderBook` requirements.

### Shift 7 — Power Flicker

Restaurant state must survive a simulated restart, unlocking JSON persistence.

### Shift 8 — Grand Opening

All unlocked systems run together under sustained load.

## Important distinction

A failure may mean one of three things:

1. an existing contract is incorrect;
2. individually valid functions interact incorrectly;
3. the restaurant now requires a new capability.

The simulator must clearly distinguish these categories.
