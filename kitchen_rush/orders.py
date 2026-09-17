"""Order creation and order lifecycle helpers."""

VALID_MVP_STATUSES = {"new", "queued", "ready", "completed"}


def create_order(order_id, table_number):
    """Create and return a new order dictionary."""
    return {
        "id": order_id,
        "table": table_number,
        # Deliberate bug: think about the operations an order needs to support.
        "items": {},
        "status": "new",
        "priority": 0,
    }


def add_item(order, menu_item, quantity):
    """Add a menu item to an order and return True on success.

    Each stored line item must keep enough information for the kitchen to prepare
    the order even if it does not look up the menu again later.
    """
    # TODO: Implement this function.
    pass


def calculate_order_total(order):
    """Return the complete order total as a float rounded to two decimals."""
    total = 0.0

    for item in order["items"]:
        # Deliberate bug: this works for one item but not every valid quantity.
        total += item["unit_price"]

    return round(total, 2)


def set_order_status(order, status):
    """Update an order to a valid MVP status and return True.

    Return False and leave the order unchanged when the status is invalid.
    """
    if status not in VALID_MVP_STATUSES:
        return False

    # Deliberate bug: this expression does not update state.
    order["status"] == status
    return True


# ---------------------------------------------------------------------------
# Post-MVP capabilities
# These functions are intentionally present from day one so the full project
# contract can exist from day one. They remain locked by the checker until the
# simulator discovers that the restaurant actually needs them.
# ---------------------------------------------------------------------------


def cancel_order(order):
    """Cancel a new or queued order. Locked until a later shift."""
    # TODO: Future requirement. Do not implement before it is unlocked unless
    # your team intentionally chooses to work ahead.
    pass


def select_next_order(queue, current_minute):
    """Return the next order that should be prepared. Locked requirement.

    Later shifts introduce urgent orders and waiting-time pressure.
    """
    # TODO: Future requirement.
    pass


class OrderBook:
    """Fast order lookup container. Locked until high-volume shifts.

    The public behavior matters more than the internal implementation.
    """

    def __init__(self):
        # Deliberate future bug: this structure makes one later operation slower
        # than the simulator will eventually tolerate.
        self._orders = []

    def add(self, order):
        # TODO: Future requirement.
        pass

    def get(self, order_id):
        # Deliberate future bug: a linear scan may be correct but eventually slow.
        for order in self._orders:
            if order.get("id") == order_id:
                return order
        return None

    def remove(self, order_id):
        # TODO: Future requirement.
        pass

    def __len__(self):
        return len(self._orders)
