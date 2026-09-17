# Architecture

## Student-owned modules

```text
app.py
kitchen_rush/
    menu.py
    orders.py
    inventory.py
    kitchen.py
    storage.py
```

### `menu.py`

Menu lookup, normalization, and item pricing.

### `orders.py`

Order creation, line items, totals, statuses, later cancellation, later priority selection, and eventually `OrderBook`.

### `inventory.py`

Ingredient availability, atomic consumption, and later reservation lifecycle.

### `kitchen.py`

Integration boundary between orders and inventory. It is intentionally where isolated functions begin interacting.

### `storage.py`

Locked until persistence becomes a real requirement.

## Curriculum-owned tooling

```text
checker.py
simulation/
tools/
docs_AI/
```

Students should normally consume these tools rather than edit them.

## Dependency direction

Prefer this direction:

```text
app / simulation
      |
      v
   kitchen
   /     \
orders  inventory
   \     /
     menu data
```

Avoid circular imports. If two modules need each other, pause and reconsider which module owns that responsibility.
