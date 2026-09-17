"""Small manual interface for the restaurant engine.

The simulator is the main game mode. This file is intentionally simple so the
team can use the restaurant manually while building the MVP.
"""

import json
from pathlib import Path

from kitchen_rush.menu import get_menu_item
from kitchen_rush.orders import add_item, calculate_order_total, create_order

ROOT = Path(__file__).parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    menu_data = load_json(ROOT / "data" / "menu.json")
    orders = []
    next_order_id = 1

    while True:
        print("\n=== KITCHEN RUSH ===")
        print("1. Create order")
        print("2. View orders")
        print("3. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            table_text = input("Table number: ").strip()
            if not table_text.isdigit():
                print("Table number must be a positive integer.")
                continue

            order = create_order(next_order_id, int(table_text))
            next_order_id += 1

            while True:
                item_name = input("Item name (blank to finish): ").strip()
                if not item_name:
                    break

                item = get_menu_item(menu_data, item_name)
                if item is None:
                    print("Item not found.")
                    continue

                quantity_text = input("Quantity: ").strip()
                if not quantity_text.isdigit() or int(quantity_text) <= 0:
                    print("Quantity must be a positive integer.")
                    continue

                if not add_item(order, item, int(quantity_text)):
                    print("Could not add item.")

            orders.append(order)
            print(f"Order #{order['id']} total: ${calculate_order_total(order):.2f}")

        elif choice == "2":
            for order in orders:
                print(order)

        elif choice == "3":
            break

        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
