"""Deterministic stress simulation for Kitchen Rush.

Shift Mode starts only after the MVP passes. Each shift increases pressure,
reveals integration defects, or introduces a new restaurant requirement.
Failures include reproducible diagnostic context: shift, day, clock, event,
order, and seed.
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from checker import run_checks
from simulation.progress import (
    complete_shift,
    load_progress,
    reset_progress,
    reveal_check,
    unlock_stage,
)

SHIFT_INFO = {
    1: ("Soft Opening", 10401),
    2: ("Shared Ingredient Trap", 18472),
    3: ("Dinner Rush", 31183),
    4: ("Change of Mind", 44004),
    5: ("VIP Night", 55105),
    6: ("Saturday Surge", 66706),
    7: ("Power Flicker", 77207),
    8: ("Grand Opening", 88808),
}


@dataclass
class EventContext:
    shift: int
    day: int
    clock: str
    event_id: int
    order_id: int | None
    seed: int


class ShiftFailure(Exception):
    def __init__(self, category, context, message, expected=None, actual=None, unlock=None, reveal=None):
        super().__init__(message)
        self.category = category
        self.context = context
        self.message = message
        self.expected = expected
        self.actual = actual
        self.unlock = unlock
        self.reveal = reveal


def clock(minute):
    minute %= 24 * 60
    return f"{minute // 60:02d}:{minute % 60:02d}"


def context(shift, event_id, seed, order_id=None, minute=12 * 60, day=1):
    return EventContext(shift, day, clock(minute), event_id, order_id, seed)


def load_data(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def engine():
    return tuple(importlib.import_module(f"kitchen_rush.{name}") for name in ("menu", "orders", "inventory", "kitchen"))


def make_order(orders_mod, menu_mod, menu_data, order_id, table, items, priority=0, created_minute=0):
    order = orders_mod.create_order(order_id, table)
    if not isinstance(order, dict):
        return order
    order["priority"] = priority
    order["created_minute"] = created_minute
    for name, quantity in items:
        item = menu_mod.get_menu_item(menu_data, name)
        if item is None or orders_mod.add_item(order, item, quantity) is not True:
            raise RuntimeError(f"Could not build order #{order_id}: {name} x{quantity}")
    return order


def stage_pass(stage):
    report = run_checks(max_stage=stage)
    target = next((s for s in report["stages"] if s["stage"] == stage), None)
    return bool(target and target["status"] == "PASS"), report


def require_previous(shift):
    if shift <= 1:
        return
    completed = set(load_progress().get("completed_shifts", []))
    if shift - 1 not in completed:
        raise SystemExit(f"Shift {shift - 1} must be completed before Shift {shift}.")


def run_shift_1(seed, until_event=None):
    menu_mod, orders_mod, inv_mod, kitchen_mod = engine()
    menu_data = load_data("menu.json")
    inventory = {"bun": 10, "patty": 10, "cheese": 10, "potato": 20, "oil": 10, "soda_can": 10}
    queue = []
    recipes = [
        (101, 1, [("Burger", 1), ("Soda", 1)]),
        (102, 3, [("Burger", 2)]),
        (103, 5, [("Fries", 2), ("Soda", 1)]),
    ]
    completed = 0
    revenue = 0.0
    for event_id, (oid, table, items) in enumerate(recipes, 1):
        ctx = context(1, event_id, seed, oid, 12 * 60 + event_id * 4)
        order = make_order(orders_mod, menu_mod, menu_data, oid, table, items)
        if kitchen_mod.queue_order(queue, order) is not True:
            raise ShiftFailure("EXISTING_CONTRACT", ctx, "A normal order could not enter the kitchen queue.", True, False)
        prepared = kitchen_mod.prepare_next_order(queue, inventory)
        if not isinstance(prepared, dict) or prepared.get("id") != oid:
            raise ShiftFailure("INTEGRATION_BUG", ctx, "A normal queued order could not be prepared.", oid, prepared)
        if kitchen_mod.complete_order(prepared) is not True:
            raise ShiftFailure("EXISTING_CONTRACT", ctx, "A ready order could not be completed.", True, False)
        completed += 1
        revenue += orders_mod.calculate_order_total(prepared)
        if until_event is not None and event_id >= until_event:
            break
    return {"orders_completed": completed, "revenue": round(revenue, 2), "inventory": inventory}


def run_shift_2(seed, until_event=None):
    menu_mod, orders_mod, inv_mod, kitchen_mod = engine()
    menu_data = load_data("menu.json")
    inventory = {"dough": 2, "tomato": 10, "cheese": 2, "bun": 2, "patty": 2}
    order = make_order(orders_mod, menu_mod, menu_data, 201, 7, [("Pizza", 1), ("Burger", 1)])
    queue = []
    ctx = context(2, 1, seed, 201, 12 * 60 + 18, day=2)
    if kitchen_mod.queue_order(queue, order) is not True:
        raise ShiftFailure("EXISTING_CONTRACT", ctx, "The shared-ingredient test order could not be queued.")
    before = copy.deepcopy(inventory)
    prepared = kitchen_mod.prepare_next_order(queue, inventory)
    if prepared is not None or inventory != before:
        reveal_check("aggregate_inventory")
        raise ShiftFailure(
            "INTEGRATION_BUG",
            ctx,
            "The order changed inventory even though the complete order could not be prepared. Two lines share the same ingredient.",
            expected={"prepared": None, "inventory": before},
            actual={"prepared": prepared, "inventory": inventory},
            reveal="aggregate_inventory",
        )
    return {"shared_inventory_guard": "passed", "inventory": inventory}


def run_shift_3(seed, until_event=None):
    menu_mod, orders_mod, inv_mod, kitchen_mod = engine()
    menu_data = load_data("menu.json")
    inventory = load_data("inventory.json")
    queue = []
    completed = 0
    event = 0
    pattern = [[("Burger", 1)], [("Fries", 1)], [("Pizza", 1)], [("Salad", 1)], [("Soda", 2)]]
    for i in range(30):
        event += 1
        oid = 300 + i
        ctx = context(3, event, seed, oid, 18 * 60 + i * 2, day=3)
        order = make_order(orders_mod, menu_mod, menu_data, oid, (i % 10) + 1, pattern[i % len(pattern)])
        if kitchen_mod.queue_order(queue, order) is not True:
            raise ShiftFailure("REGRESSION", ctx, "An ordinary dinner-rush order could not be queued.")
        prepared = kitchen_mod.prepare_next_order(queue, inventory)
        if prepared is None:
            if not queue or queue[0].get("id") != oid:
                raise ShiftFailure("STATE_BUG", ctx, "An unprepared order disappeared from the queue.")
            break
        if kitchen_mod.complete_order(prepared) is not True:
            raise ShiftFailure("STATE_BUG", ctx, "A prepared dinner-rush order could not complete.")
        completed += 1
        if until_event is not None and event >= until_event:
            break
    return {"orders_completed": completed, "events": event, "remaining_queue": len(queue)}


def run_shift_4(seed, until_event=None):
    unlock_stage(5)
    ok, _ = stage_pass(5)
    if not ok:
        raise ShiftFailure(
            "NEW_REQUIREMENT",
            context(4, 1, seed, 401, 16 * 60 + 40, day=4),
            "A customer cancelled after the kitchen accepted the order. The restaurant now needs reversible reservations and cancellation.",
            expected="Stage 5 checker contracts pass",
            actual="Stage 5 is incomplete",
            unlock=5,
        )
    menu_mod, orders_mod, inv_mod, kitchen_mod = engine()
    menu_data = load_data("menu.json")
    inventory = {"bun": 5, "patty": 5, "cheese": 5}
    reservations = {}
    queue = []
    order = make_order(orders_mod, menu_mod, menu_data, 401, 2, [("Burger", 2)])
    before = copy.deepcopy(inventory)
    if kitchen_mod.submit_order(queue, inventory, reservations, order) is not True:
        raise ShiftFailure("EXISTING_CONTRACT", context(4, 2, seed, 401), "Reservation submission failed.")
    if kitchen_mod.cancel_queued_order(queue, inventory, reservations, 401) is not True:
        raise ShiftFailure("EXISTING_CONTRACT", context(4, 3, seed, 401), "Cancellation failed after reservation.")
    if inventory != before or queue or reservations or order.get("status") != "cancelled":
        raise ShiftFailure("STATE_BUG", context(4, 4, seed, 401), "Cancellation did not completely roll back restaurant state.", {"inventory": before, "queue": [], "reservations": {}, "status": "cancelled"}, {"inventory": inventory, "queue": queue, "reservations": reservations, "status": order.get("status")})
    return {"cancellation": "clean rollback"}


def run_shift_5(seed, until_event=None):
    unlock_stage(6)
    ok, _ = stage_pass(6)
    if not ok:
        raise ShiftFailure("NEW_REQUIREMENT", context(5, 1, seed, 502, 19 * 60 + 5, day=5), "VIP orders and waiting time now affect which order should cook next.", "Stage 6 checker contracts pass", "Stage 6 is incomplete", unlock=6)
    menu_mod, orders_mod, inv_mod, kitchen_mod = engine()
    menu_data = load_data("menu.json")
    inventory = {"bun": 10, "patty": 10, "cheese": 10}
    reservations = {}; queue = []
    normal = make_order(orders_mod, menu_mod, menu_data, 501, 1, [("Burger", 1)], priority=0, created_minute=5)
    vip = make_order(orders_mod, menu_mod, menu_data, 502, 2, [("Burger", 1)], priority=10, created_minute=15)
    for o in (normal, vip):
        if kitchen_mod.submit_order(queue, inventory, reservations, o) is not True:
            raise ShiftFailure("EXISTING_CONTRACT", context(5, 2, seed, o["id"]), "Could not submit a priority-shift order.")
    prepared = kitchen_mod.prepare_reserved_order(queue, reservations, 30)
    if not isinstance(prepared, dict) or prepared.get("id") != 502:
        raise ShiftFailure("POLICY_BUG", context(5, 3, seed, 502, 19 * 60 + 8, day=5), "The urgent order was not selected first.", 502, prepared.get("id") if isinstance(prepared, dict) else prepared)
    return {"first_prepared": prepared["id"]}


def run_shift_6(seed, until_event=None):
    unlock_stage(7)
    ok, _ = stage_pass(7)
    if not ok:
        raise ShiftFailure("NEW_REQUIREMENT", context(6, 1, seed, None, 13 * 60, day=6), "The restaurant now tracks thousands of orders. Correct linear lookup is no longer fast enough.", "Stage 7 OrderBook behavior and performance pass", "Stage 7 is incomplete or too slow", unlock=7)
    from kitchen_rush.orders import OrderBook
    book = OrderBook(); started = time.perf_counter()
    for oid in range(10000, 15000):
        book.add({"id": oid, "table": oid % 20 + 1, "items": [], "status": "completed", "priority": 0, "created_minute": 0})
    for oid in range(14999, 13999, -1):
        if book.get(oid) is None:
            raise ShiftFailure("INVARIANT_BROKEN", context(6, oid - 13999, seed, oid), "OrderBook lost an order during the surge.")
    return {"tracked_orders": len(book), "surge_seconds": round(time.perf_counter() - started, 5)}


def run_shift_7(seed, until_event=None):
    unlock_stage(8)
    ok, _ = stage_pass(8)
    if not ok:
        raise ShiftFailure("NEW_REQUIREMENT", context(7, 1, seed, 701, 20 * 60 + 17, day=7), "A power flicker restarts the process. Restaurant state must survive using JSON persistence.", "Stage 8 persistence contracts pass", "Stage 8 is incomplete", unlock=8)
    import tempfile
    from kitchen_rush.storage import load_state, save_state
    state = {"inventory": {"bun": 9, "cheese": 4}, "next_order_id": 702, "orders": [{"id": 701, "table": 1, "items": [], "status": "completed", "priority": 0, "created_minute": 0}]}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "restaurant-state.json"
        if save_state(path, copy.deepcopy(state)) is not True or load_state(path) != state:
            raise ShiftFailure("INVARIANT_BROKEN", context(7, 2, seed, 701, 20 * 60 + 18, day=7), "Restarted state does not match the state before the power flicker.", state, load_state(path))
    return {"restart_recovery": "passed"}


def run_shift_8(seed, until_event=None):
    ok, _ = stage_pass(8)
    if not ok:
        raise ShiftFailure("EXISTING_CONTRACT", context(8, 1, seed, day=8), "Grand Opening requires every unlocked checker stage to pass.")
    summary = {
        "soft_opening": run_shift_1(seed + 1),
        "shared_inventory": run_shift_2(seed + 2),
        "dinner_rush": run_shift_3(seed + 3),
        "cancellations": run_shift_4(seed + 4),
        "priority": run_shift_5(seed + 5),
        "scale": run_shift_6(seed + 6),
        "persistence": run_shift_7(seed + 7),
    }
    return summary


RUNNERS = {1: run_shift_1, 2: run_shift_2, 3: run_shift_3, 4: run_shift_4, 5: run_shift_5, 6: run_shift_6, 7: run_shift_7, 8: run_shift_8}


def print_failure(failure):
    c = failure.context
    print("\n" + "=" * 68); print("SHIFT FAILURE"); print("=" * 68)
    print(f"Category: {failure.category}")
    print(f"Shift: {c.shift} — {SHIFT_INFO[c.shift][0]}")
    print(f"Day: {c.day}"); print(f"Time: {c.clock}"); print(f"Event: #{c.event_id}")
    if c.order_id is not None: print(f"Order: #{c.order_id}")
    print(f"Seed: {c.seed}\n"); print(failure.message)
    if failure.expected is not None: print("\nExpected:\n" + json.dumps(failure.expected, indent=2, default=str))
    if failure.actual is not None: print("\nActual:\n" + json.dumps(failure.actual, indent=2, default=str))
    if failure.unlock:
        print(f"\nNEW CHECKER STAGE UNLOCKED: Stage {failure.unlock}"); print("Run: python checker.py")
    if failure.reveal:
        print("\nA new integration check is now visible."); print("Run: python checker.py")


def run_one(shift_number, seed=None, until_event=None):
    require_previous(shift_number)
    name, default_seed = SHIFT_INFO[shift_number]; seed = default_seed if seed is None else seed
    if shift_number <= 3:
        mvp = run_checks(max_stage=4)
        if not mvp["mvp_pass"]:
            print("The MVP is not ready for Shift Mode yet.\n\nRun: python checker.py")
            return False
    print("=" * 68); print(f"SHIFT {shift_number} — {name}"); print(f"Seed: {seed}"); print("=" * 68)
    try:
        summary = RUNNERS[shift_number](seed, until_event)
    except ShiftFailure as failure:
        print_failure(failure); return False
    except Exception as exc:
        print_failure(ShiftFailure("UNEXPECTED_CRASH", context(shift_number, 0, seed), f"The simulation crashed with {type(exc).__name__}: {exc}")); return False
    if until_event is None: complete_shift(shift_number, seed)
    print("\nSHIFT COMPLETE"); print(json.dumps(summary, indent=2, default=str))
    if shift_number < 8 and until_event is None: print(f"\nNext: python simulation/shift.py --shift {shift_number + 1}")
    return True


def print_status():
    state = load_progress(); print("KITCHEN RUSH SHIFT STATUS"); print(f"Unlocked checker stage: {state['unlocked_stage']}"); print(f"Completed shifts: {state['completed_shifts'] or 'none'}"); print(f"Revealed integration checks: {state['revealed_checks'] or 'none'}")
    completed = set(state["completed_shifts"])
    for number, (name, _) in SHIFT_INFO.items():
        ready = number == 1 or number - 1 in completed
        marker = "DONE" if number in completed else ("READY" if ready else "LOCKED")
        print(f"  Shift {number}: {name} [{marker}]")


def main():
    parser = argparse.ArgumentParser(description="Run deterministic Kitchen Rush shifts.")
    parser.add_argument("--shift", type=int, choices=range(1, 9)); parser.add_argument("--seed", type=int); parser.add_argument("--until-event", type=int); parser.add_argument("--status", action="store_true"); parser.add_argument("--reset-progress", action="store_true")
    args = parser.parse_args()
    if args.reset_progress:
        reset_progress(); print("Local Kitchen Rush progress reset.")
        if not args.shift and not args.status: return
    if args.status:
        print_status()
        if not args.shift: return
    if args.shift is None: parser.error("Choose --shift N or --status.")
    raise SystemExit(0 if run_one(args.shift, args.seed, args.until_event) else 1)


if __name__ == "__main__":
    main()
