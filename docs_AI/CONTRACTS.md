# Public Contracts

This file documents public behavior without prescribing implementation.

## MVP contracts

### Menu

`normalize_item_name(name) -> str`

Normalize surrounding whitespace and case.

`get_menu_item(menu_data, name) -> dict | None`

Find a menu item case-insensitively after normalization.

`calculate_item_price(item, quantity) -> float`

Return `0.0` for non-positive quantities.

### Orders

`create_order(order_id, table_number) -> dict`

Expected minimum shape:

```python
{
    "id": 1,
    "table": 4,
    "items": [],
    "status": "new",
    "priority": 0,
}
```

`add_item(order, menu_item, quantity) -> bool`

Store name, unit price, quantity, and ingredient requirements in each order line.

`calculate_order_total(order) -> float`

`set_order_status(order, status) -> bool`

MVP statuses: `new`, `queued`, `ready`, `completed`.

### Inventory

`has_ingredients(inventory, menu_item, quantity) -> bool`

`consume_ingredients(inventory, menu_item, quantity) -> bool`

Consumption must be atomic: failed consumption cannot partially change inventory.

### Kitchen

`can_prepare_order(order, inventory) -> bool`

This contract applies to the whole order, not only each line independently.

`queue_order(queue, order) -> bool`

`prepare_next_order(queue, inventory) -> dict | None`

`complete_order(order) -> bool`

## Locked post-MVP contracts

The checker reveals these progressively as the simulator discovers new restaurant requirements.

- order cancellation;
- inventory reservations and release;
- reserved-order submission and cancellation;
- priority-based next-order selection;
- `OrderBook` indexed access;
- JSON persistence.

Do not assume a locked capability is required for the current stage.
