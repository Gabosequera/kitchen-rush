"""Inventory checks and mutations."""


def has_ingredients(inventory, menu_item, quantity):
    """Return True only when all required ingredients are available."""
    if quantity <= 0:
        return False

    for ingredient, amount_per_item in menu_item["ingredients"].items():
        required = amount_per_item * quantity

        # Deliberate bug: exact stock should still be enough.
        if inventory.get(ingredient, 0) <= required:
            return False

    return True


def consume_ingredients(inventory, menu_item, quantity):
    """Atomically consume ingredients and return True.

    If the item cannot be prepared, inventory must not change.
    """
    if not has_ingredients(inventory, menu_item, quantity):
        return False

    for ingredient, amount_per_item in menu_item["ingredients"].items():
        inventory[ingredient] -= amount_per_item * quantity

    return True


# ---------------------------------------------------------------------------
# Post-MVP reservation system
# ---------------------------------------------------------------------------


def reserve_order(inventory, reservations, order):
    """Reserve all ingredients for an order atomically. Locked requirement."""
    # TODO: Future requirement.
    pass


def release_order(inventory, reservations, order_id):
    """Release a reservation back into inventory. Locked requirement."""
    # TODO: Future requirement.
    pass


def consume_reservation(reservations, order_id):
    """Finalize a reservation without restoring stock. Locked requirement."""
    # TODO: Future requirement.
    pass
