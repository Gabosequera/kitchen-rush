"""Kitchen queue and integration logic.

This module intentionally contains a bug that is harder to see in isolated
function tests. The simulator will eventually create the conditions that expose it.
"""

from kitchen_rush.inventory import consume_ingredients, has_ingredients
from kitchen_rush.orders import set_order_status


def _line_as_menu_item(line):
    return {
        "name": line["name"],
        "price": line["unit_price"],
        "ingredients": line["ingredients"],
    }


def can_prepare_order(order, inventory):
    """Return True when the whole order can be prepared with current stock."""
    # Deliberate integration bug:
    # Each line is checked independently against the same inventory snapshot.
    # This can be wrong when multiple lines need the same ingredient.
    for line in order["items"]:
        menu_item = _line_as_menu_item(line)
        if not has_ingredients(inventory, menu_item, line["quantity"]):
            return False

    return True


def queue_order(queue, order):
    """Append a new order to the kitchen queue and mark it queued."""
    if order.get("status") != "new":
        return False

    queue.append(order)
    return set_order_status(order, "queued")


def prepare_next_order(queue, inventory):
    """Prepare the first queued order and return it, or return None."""
    if not queue:
        return None

    order = queue[0]

    if not can_prepare_order(order, inventory):
        return None

    # This loop becomes dangerous if can_prepare_order() gave a false positive.
    for line in order["items"]:
        menu_item = _line_as_menu_item(line)
        if not consume_ingredients(inventory, menu_item, line["quantity"]):
            return None

    queue.pop(0)
    set_order_status(order, "ready")
    return order


def complete_order(order):
    """Complete a ready order and return True on success."""
    if order.get("status") != "ready":
        return False
    return set_order_status(order, "completed")


# ---------------------------------------------------------------------------
# Post-MVP kitchen flow
# ---------------------------------------------------------------------------


def submit_order(queue, inventory, reservations, order):
    """Reserve ingredients and submit an order. Locked requirement."""
    # TODO: Future requirement.
    pass


def cancel_queued_order(queue, inventory, reservations, order_id):
    """Cancel a queued order and release its reservation. Locked requirement."""
    # TODO: Future requirement.
    pass


def prepare_reserved_order(queue, reservations, current_minute):
    """Prepare the correct reserved order. Locked priority requirement."""
    # TODO: Future requirement.
    pass
