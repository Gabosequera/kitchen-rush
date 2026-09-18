"""Menu helpers.

This file starts with a mix of incomplete code and deliberate beginner-level bugs.
Do not assume that code is correct just because it already exists.
"""


def normalize_item_name(name):
    """Return a normalized menu item name.

    Expected examples:
        "Burger" -> "burger"
        "  PIZZA  " -> "pizza"
    """
    # Deliberate bug: this implementation misses one small normalization step.
    return name.lower().strip()


def get_menu_item(menu_data, name):
    """Return the matching menu item dictionary, or None if it does not exist."""
    # TODO: Implement this function.

    for item in menu_data:
        if item["name"].lower() == name.strip().lower():
            return item
        else: return None

def calculate_item_price(item, quantity):
    """Return the price for a quantity of one menu item as a float.

    Non-positive quantities should return 0.0.
    """
    if quantity <= 0:
        return 0.0

    total = item["price"] * quantity
    # Deliberate bug: the value looks correct when printed, but its type is wrong.
    return total
