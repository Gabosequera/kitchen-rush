"""Curriculum-aware behavioral checker for Kitchen Rush.

This tooling is intentionally more advanced than the student code. It checks
observable contracts, survives missing/incomplete work, and progressively
reveals post-MVP requirements as Shift Mode discovers them.
"""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / ".kitchen_rush" / "progress.json"


@dataclass
class CheckResult:
    stage: int
    check_id: str
    label: str
    status: str
    message: str
    expected: Any = None
    received: Any = None
    example: Any = None


@dataclass
class Stage:
    number: int
    name: str
    description: str
    checks: list[Callable[[], CheckResult]]


_CACHE: dict[str, Any] = {}


def load_progress():
    default = {"unlocked_stage": 4, "completed_shifts": [], "revealed_checks": [], "last_seed": None}
    if not PROGRESS_FILE.exists():
        return default
    try:
        return {**default, **json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))}
    except (OSError, json.JSONDecodeError):
        return default


def member(module_name, name):
    if module_name not in _CACHE:
        try:
            _CACHE[module_name] = importlib.import_module(f"kitchen_rush.{module_name}")
        except Exception as exc:
            _CACHE[module_name] = exc
    module = _CACHE[module_name]
    if isinstance(module, Exception):
        return None, f"Import failed: {type(module).__name__}: {module}"
    if not hasattr(module, name):
        return None, f"Missing {name!r} in kitchen_rush/{module_name}.py"
    return getattr(module, name), None


def out(stage, cid, label, ok, message, expected=None, received=None, example=None):
    return CheckResult(stage, cid, label, "PASS" if ok else "FAIL", message, expected, received, example)


def missing(stage, cid, label, message, example=None):
    return CheckResult(stage, cid, label, "MISSING", message, example=example)


def safe(stage, cid, label, fn, action, expected=None, example=None):
    if fn is None:
        return None
    try:
        return action()
    except Exception as exc:
        return CheckResult(stage, cid, label, "FAIL", f"The code raised {type(exc).__name__}: {exc}", expected, {"exception": type(exc).__name__, "message": str(exc)}, example)


def menu_fixture():
    return [
        {"name": "Burger", "price": 8.5, "ingredients": {"bun": 1, "patty": 1, "cheese": 1}},
        {"name": "Pizza", "price": 10.0, "ingredients": {"dough": 1, "tomato": 2, "cheese": 2}},
        {"name": "Soda", "price": 2.0, "ingredients": {"soda_can": 1}},
    ]


def line(name, price, quantity, ingredients):
    return {"name": name, "unit_price": price, "quantity": quantity, "ingredients": ingredients}


def order(order_id=1, table=1, items=None, status="new", priority=0, created_minute=0):
    return {"id": order_id, "table": table, "items": list(items or []), "status": status, "priority": priority, "created_minute": created_minute}


# Stage 1 ------------------------------------------------------------------
def check_normalize():
    fn, err = member("menu", "normalize_item_name"); label = "Normalize menu item names"
    if err: return missing(1, "menu.normalize", label, err)
    try: value = fn("  PIZZA  ")
    except Exception as exc: return out(1,"menu.normalize",label,False,f"Raised {type(exc).__name__}: {exc}","pizza")
    return out(1,"menu.normalize",label,isinstance(value,str) and value=="pizza","Names must ignore surrounding whitespace and case.",{"type":"str","value":"pizza"},{"type":type(value).__name__,"value":value})


def check_lookup():
    fn, err = member("menu", "get_menu_item"); label = "Find a menu item"
    if err: return missing(1,"menu.lookup",label,err)
    try:
        found=fn(copy.deepcopy(menu_fixture())," burger "); absent=fn(copy.deepcopy(menu_fixture()),"ramen")
    except Exception as exc: return out(1,"menu.lookup",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=isinstance(found,dict) and found.get("name")=="Burger" and absent is None
    return out(1,"menu.lookup",label,ok,"Lookup must normalize names and return None when absent.",{"found":"Burger dictionary","missing":None},{"found":found,"missing":absent})


def check_price():
    fn, err = member("menu", "calculate_item_price"); label="Calculate item price"
    if err: return missing(1,"menu.price",label,err)
    try: a=fn(copy.deepcopy(menu_fixture()[0]),2); z=fn(copy.deepcopy(menu_fixture()[0]),0)
    except Exception as exc: return out(1,"menu.price",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=isinstance(a,float) and a==17.0 and isinstance(z,float) and z==0.0
    return out(1,"menu.price",label,ok,"The numeric value and return type both matter.",{"quantity_2":17.0,"quantity_0":0.0},{"quantity_2":{"type":type(a).__name__,"value":a},"quantity_0":z})


# Stage 2 ------------------------------------------------------------------
def check_create_order():
    fn,err=member("orders","create_order"); label="Create a new order"
    if err:return missing(2,"orders.create",label,err)
    try:v=fn(12,4)
    except Exception as exc:return out(2,"orders.create",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=isinstance(v,dict) and v.get("id")==12 and v.get("table")==4 and isinstance(v.get("items"),list) and v.get("status")=="new" and v.get("priority")==0
    return out(2,"orders.create",label,ok,"The order shape must be usable by other modules.",{"id":12,"table":4,"items":[],"status":"new","priority":0},v)


def check_add_item():
    fn,err=member("orders","add_item"); label="Add an item to an order"
    if err:return missing(2,"orders.add_item",label,err)
    o=order(); item=menu_fixture()[0]
    try:r=fn(o,copy.deepcopy(item),2)
    except Exception as exc:return out(2,"orders.add_item",label,False,f"Raised {type(exc).__name__}: {exc}")
    stored=o.get("items"); first=stored[0] if isinstance(stored,list) and stored else None
    ok=r is True and isinstance(first,dict) and first==line("Burger",8.5,2,item["ingredients"])
    return out(2,"orders.add_item",label,ok,"Store enough line information for the kitchen to work without another menu lookup.",{"return":True,"line":line("Burger",8.5,2,item["ingredients"])},{"return":r,"items":stored})


def check_total():
    fn,err=member("orders","calculate_order_total"); label="Calculate an order total"
    if err:return missing(2,"orders.total",label,err)
    o=order(items=[line("Burger",8.5,2,{"bun":1}),line("Soda",2.0,1,{"soda_can":1})])
    try:v=fn(o)
    except Exception as exc:return out(2,"orders.total",label,False,f"Raised {type(exc).__name__}: {exc}")
    return out(2,"orders.total",label,isinstance(v,float) and v==19.0,"Totals must include quantity.",19.0,{"type":type(v).__name__,"value":v})


def check_status():
    fn,err=member("orders","set_order_status"); label="Update order status"
    if err:return missing(2,"orders.status",label,err)
    o=order(); before=copy.deepcopy(o)
    try:a=fn(o,"queued"); good=o.get("status"); b=fn(o,"teleported"); after=o.get("status")
    except Exception as exc:return out(2,"orders.status",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=a is True and good=="queued" and b is False and after=="queued"
    return out(2,"orders.status",label,ok,"Valid transitions change state; invalid statuses must not.",{"queued_return":True,"status":"queued","invalid_return":False},{"queued_return":a,"status_after_valid":good,"invalid_return":b,"status_after_invalid":after,"before":before})


# Stage 3 ------------------------------------------------------------------
def check_inventory_available():
    fn,err=member("inventory","has_ingredients"); label="Check ingredient availability"
    if err:return missing(3,"inventory.available",label,err)
    item={"name":"Burger","ingredients":{"bun":1,"patty":1}}
    try:exact=fn({"bun":2,"patty":2},item,2); short=fn({"bun":2,"patty":1},item,2); invalid=fn({"bun":10,"patty":10},item,0)
    except Exception as exc:return out(3,"inventory.available",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=exact is True and short is False and invalid is False
    return out(3,"inventory.available",label,ok,"Exact stock is enough; insufficient or non-positive requests are not.",{"exact":True,"short":False,"quantity_0":False},{"exact":exact,"short":short,"quantity_0":invalid})


def check_inventory_consume():
    fn,err=member("inventory","consume_ingredients"); label="Consume inventory atomically"
    if err:return missing(3,"inventory.consume",label,err)
    item={"name":"Burger","ingredients":{"bun":1,"patty":1}}
    good={"bun":4,"patty":4}; bad={"bun":4,"patty":1}; bad_before=copy.deepcopy(bad)
    try:r1=fn(good,item,2); r2=fn(bad,item,2)
    except Exception as exc:return out(3,"inventory.consume",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=r1 is True and good=={"bun":2,"patty":2} and r2 is False and bad==bad_before
    return out(3,"inventory.consume",label,ok,"Failed consumption must not partially mutate inventory.",{"success_inventory":{"bun":2,"patty":2},"failed_inventory":bad_before},{"success_return":r1,"success_inventory":good,"failed_return":r2,"failed_inventory":bad})


# Stage 4 ------------------------------------------------------------------
def check_kitchen_basic():
    fn,err=member("kitchen","can_prepare_order"); label="Check a complete order"
    if err:return missing(4,"kitchen.can_prepare",label,err)
    o=order(items=[line("Burger",8.5,1,{"bun":1,"patty":1})])
    try:a=fn(o,{"bun":1,"patty":1}); b=fn(o,{"bun":1,"patty":0})
    except Exception as exc:return out(4,"kitchen.can_prepare",label,False,f"Raised {type(exc).__name__}: {exc}")
    return out(4,"kitchen.can_prepare",label,a is True and b is False,"Kitchen availability should represent the whole order.",{"enough":True,"short":False},{"enough":a,"short":b})


def check_queue():
    fn,err=member("kitchen","queue_order"); label="Queue a new order"
    if err:return missing(4,"kitchen.queue",label,err)
    q=[]; o=order(8)
    try:r=fn(q,o)
    except Exception as exc:return out(4,"kitchen.queue",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=r is True and q==[o] and o.get("status")=="queued"
    return out(4,"kitchen.queue",label,ok,"Queueing must append exactly once and update status.",{"return":True,"queue_length":1,"status":"queued"},{"return":r,"queue":q,"status":o.get("status")})


def check_prepare_complete():
    prepare,e1=member("kitchen","prepare_next_order"); complete,e2=member("kitchen","complete_order"); label="Prepare and complete an order"
    if e1 or e2:return missing(4,"kitchen.lifecycle",label,e1 or e2)
    q=[order(9,items=[line("Burger",8.5,1,{"bun":1,"patty":1})],status="queued")]; inv={"bun":2,"patty":2}
    try:p=prepare(q,inv); c=complete(p) if isinstance(p,dict) else None
    except Exception as exc:return out(4,"kitchen.lifecycle",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=isinstance(p,dict) and p.get("id")==9 and p.get("status")=="completed" and q==[] and inv=={"bun":1,"patty":1} and c is True
    return out(4,"kitchen.lifecycle",label,ok,"A prepared order leaves the queue, consumes stock, becomes ready, then can complete.",{"queue":[],"inventory":{"bun":1,"patty":1},"status":"completed"},{"prepared":p,"complete_return":c,"queue":q,"inventory":inv})


def check_aggregate_inventory():
    fn,err=member("kitchen","can_prepare_order"); label="Account for shared ingredients across the whole order"
    if err:return missing(4,"kitchen.aggregate_inventory",label,err)
    o=order(items=[line("Pizza",10.0,1,{"cheese":2}),line("Burger",8.5,1,{"cheese":1})])
    try:v=fn(o,{"cheese":2})
    except Exception as exc:return out(4,"kitchen.aggregate_inventory",label,False,f"Raised {type(exc).__name__}: {exc}")
    return out(4,"kitchen.aggregate_inventory",label,v is False,"Two lines can be individually valid but collectively require more of the same ingredient than exists.",False,v)


# Stage 5 ------------------------------------------------------------------
def check_cancel_order():
    fn,err=member("orders","cancel_order"); label="Cancel an order"
    if err:return missing(5,"orders.cancel",label,err)
    for status in ("new","queued"):
        o=order(status=status)
        try:r=fn(o)
        except Exception as exc:return out(5,"orders.cancel",label,False,f"Raised {type(exc).__name__}: {exc}")
        if r is not True or o.get("status")!="cancelled": return out(5,"orders.cancel",label,False,"New and queued orders must become cancelled.",True,{"return":r,"status":o.get("status")})
    o=order(status="completed"); before=copy.deepcopy(o); r=fn(o)
    return out(5,"orders.cancel",label,r is False and o==before,"Completed orders cannot be cancelled.",False,{"return":r,"order":o})


def check_reservations():
    reserve,e1=member("inventory","reserve_order"); release,e2=member("inventory","release_order"); consume,e3=member("inventory","consume_reservation"); label="Reserve, release, and consume ingredients"
    if e1 or e2 or e3:return missing(5,"inventory.reservations",label,e1 or e2 or e3)
    inv={"bun":3,"patty":3}; res={}; o=order(44,items=[line("Burger",8.5,2,{"bun":1,"patty":1})],status="queued")
    try:a=reserve(inv,res,o); after=copy.deepcopy(inv); b=release(inv,res,44); restored=copy.deepcopy(inv); c=reserve(inv,res,o); d=consume(res,44)
    except Exception as exc:return out(5,"inventory.reservations",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=a is True and after=={"bun":1,"patty":1} and b is True and restored=={"bun":3,"patty":3} and c is True and d is True and 44 not in res
    return out(5,"inventory.reservations",label,ok,"Reservations remove stock atomically; release restores it; consume finalizes without restoring.",{"reserved_inventory":{"bun":1,"patty":1},"restored":{"bun":3,"patty":3}},{"reserve":a,"reserved_inventory":after,"release":b,"restored":restored,"consume":d,"reservations":res})


def check_submit_cancel():
    submit,e1=member("kitchen","submit_order"); cancel,e2=member("kitchen","cancel_queued_order"); label="Submit and cancel a reserved kitchen order"
    if e1 or e2:return missing(5,"kitchen.reserved_flow",label,e1 or e2)
    inv={"bun":3,"patty":3}; res={}; q=[]; o=order(55,items=[line("Burger",8.5,2,{"bun":1,"patty":1})])
    try:a=submit(q,inv,res,o); b=cancel(q,inv,res,55)
    except Exception as exc:return out(5,"kitchen.reserved_flow",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=a is True and b is True and q==[] and inv=={"bun":3,"patty":3} and res=={} and o.get("status")=="cancelled"
    return out(5,"kitchen.reserved_flow",label,ok,"Cancellation must roll back queue and reserved inventory consistently.",{"queue":[],"inventory":{"bun":3,"patty":3},"reservations":{},"status":"cancelled"},{"submit":a,"cancel":b,"queue":q,"inventory":inv,"reservations":res,"status":o.get("status")})


# Stage 6 ------------------------------------------------------------------
def check_priority():
    select,e1=member("orders","select_next_order"); prepare,e2=member("kitchen","prepare_reserved_order"); label="Select urgent and aging orders predictably"
    if e1 or e2:return missing(6,"orders.priority",label,e1 or e2)
    normal=order(1,status="queued",priority=0,created_minute=5); vip=order(2,status="queued",priority=10,created_minute=15)
    q=[normal,vip]
    try:s=select(q,30)
    except Exception as exc:return out(6,"orders.priority",label,False,f"Raised {type(exc).__name__}: {exc}")
    if not isinstance(s,dict) or s.get("id")!=2:return out(6,"orders.priority",label,False,"Higher priority should win when waiting time does not outweigh it.",2,s.get("id") if isinstance(s,dict) else s)
    res={1:{},2:{}}
    try:p=prepare(q,res,30)
    except Exception as exc:return out(6,"orders.priority",label,False,f"prepare_reserved_order raised {type(exc).__name__}: {exc}")
    ok=isinstance(p,dict) and p.get("id")==2 and p.get("status")=="ready" and 2 not in res and all(x.get("id")!=2 for x in q)
    return out(6,"orders.priority",label,ok,"Preparing the selected order must also update queue, reservation, and status.",{"prepared_id":2,"status":"ready"},{"prepared":p,"queue":q,"reservations":res})


# Stage 7 ------------------------------------------------------------------
def check_order_book():
    cls,err=member("orders","OrderBook"); label="Manage orders through OrderBook"
    if err:return missing(7,"orders.order_book",label,err)
    try:
        b=cls(); one=order(1); two=order(2); a=b.add(one); c=b.add(two); dup=b.add(copy.deepcopy(one)); got=b.get(2); removed=b.remove(1); gone=b.get(1); length=len(b)
    except Exception as exc:return out(7,"orders.order_book",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=a is True and c is True and dup is False and got is two and removed is one and gone is None and length==1
    return out(7,"orders.order_book",label,ok,"OrderBook must reject duplicate IDs and keep add/get/remove consistent.",{"add":[True,True],"duplicate":False,"get_2":"order #2","remove_1":"order #1","len":1},{"add":[a,c],"duplicate":dup,"get_2":got,"remove_1":removed,"get_1":gone,"len":length})


def check_order_book_perf():
    cls,err=member("orders","OrderBook"); label="Keep high-volume lookup responsive"
    if err:return missing(7,"orders.order_book_perf",label,err)
    try:
        b=cls(); count=5000
        for i in range(count):
            if b.add(order(i)) is not True:return out(7,"orders.order_book_perf",label,False,"Could not load benchmark orders.")
        started=time.perf_counter()
        for _ in range(1200):
            v=b.get(count-1)
            if not isinstance(v,dict) or v.get("id")!=count-1:return out(7,"orders.order_book_perf",label,False,"Lookup returned the wrong order.")
        elapsed=time.perf_counter()-started
    except Exception as exc:return out(7,"orders.order_book_perf",label,False,f"Raised {type(exc).__name__}: {exc}")
    threshold=0.10
    return out(7,"orders.order_book_perf",label,elapsed<threshold,f"Benchmark: {elapsed:.4f}s; target is below {threshold:.2f}s.",{"max_seconds":threshold},{"seconds":round(elapsed,6)},"Use a structure that can find an ID without scanning every order.")


# Stage 8 ------------------------------------------------------------------
def check_storage():
    save,e1=member("storage","save_state"); load,e2=member("storage","load_state"); label="Persist and restore restaurant state"
    if e1 or e2:return missing(8,"storage.json",label,e1 or e2)
    state={"inventory":{"bun":4,"cheese":2},"orders":[order(4,table=8,status="queued")],"next_order_id":5}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"state.json"; saved=save(path,copy.deepcopy(state)); loaded=load(path); missing_value=load(Path(tmp)/"missing.json")
            try: valid=json.loads(path.read_text(encoding="utf-8"))==state
            except Exception: valid=False
    except Exception as exc:return out(8,"storage.json",label,False,f"Raised {type(exc).__name__}: {exc}")
    ok=saved is True and loaded==state and missing_value is None and valid
    return out(8,"storage.json",label,ok,"State must round-trip as valid JSON and missing files return None.",{"save":True,"round_trip":True,"missing":None,"valid_json":True},{"save":saved,"loaded":loaded,"missing":missing_value,"valid_json":valid})


STAGES=[
    Stage(1,"Menu Foundations","Functions, strings, returns, and basic conditions.",[check_normalize,check_lookup,check_price]),
    Stage(2,"Orders","Lists, dictionaries, loops, and state mutation.",[check_create_order,check_add_item,check_total,check_status]),
    Stage(3,"Inventory","Validation and atomic state changes.",[check_inventory_available,check_inventory_consume]),
    Stage(4,"Kitchen Integration / MVP","Modules interacting through shared contracts.",[check_kitchen_basic,check_queue,check_prepare_complete]),
    Stage(5,"Cancellation & Reservations","Reversible state and transactional thinking.",[check_cancel_order,check_reservations,check_submit_cancel]),
    Stage(6,"Priority Pressure","Queue policy, selection, and tie-breaking.",[check_priority]),
    Stage(7,"OrderBook & Scale","OOP and data structures introduced by performance pressure.",[check_order_book,check_order_book_perf]),
    Stage(8,"Persistence","JSON, file I/O, and restart recovery.",[check_storage]),
]


def run_checks(max_stage=None,reveal_all=False):
    global _CACHE; _CACHE={}
    progress=load_progress(); unlocked=8 if reveal_all else int(progress.get("unlocked_stage",4))
    if max_stage is not None: unlocked=min(unlocked,max_stage)
    reports=[]; visible=[]
    for stage in STAGES:
        if stage.number>unlocked:
            reports.append({"stage":stage.number,"name":stage.name,"description":stage.description,"status":"LOCKED","results":[]}); continue
        checks=list(stage.checks)
        if stage.number==4 and (reveal_all or "aggregate_inventory" in progress.get("revealed_checks",[])): checks.append(check_aggregate_inventory)
        results=[fn() for fn in checks]; visible.extend(results)
        reports.append({"stage":stage.number,"name":stage.name,"description":stage.description,"status":"PASS" if all(r.status=="PASS" for r in results) else "FAIL","results":[asdict(r) for r in results]})
    mvp=[r for r in visible if r.stage<=4]
    return {"visible_pass":bool(visible) and all(r.status=="PASS" for r in visible),"mvp_pass":bool(mvp) and all(r.status=="PASS" for r in mvp),"unlocked_stage":unlocked,"progress":progress,"stages":reports}


def pretty(value):
    if isinstance(value,str): return value
    return json.dumps(value,indent=2,ensure_ascii=False,default=str)


def indent(text,n=4):
    p=" "*n; return "\n".join(p+x for x in str(text).splitlines())


def print_report(report):
    print("="*68); print("KITCHEN RUSH CHECKER"); print("="*68)
    for stage in report["stages"]:
        print(f"\nSTAGE {stage['stage']} — {stage['name']}"); print(stage["description"])
        if stage["status"]=="LOCKED": print("[LOCKED] The restaurant has not discovered this requirement yet."); continue
        for item in stage["results"]:
            print(f"[{item['status']}] {item['label']}")
            if item["status"]!="PASS":
                print("  "+item["message"])
                if item.get("expected") is not None: print("  Expected:\n"+indent(pretty(item["expected"])))
                if item.get("received") is not None: print("  Received:\n"+indent(pretty(item["received"])))
                if item.get("example") is not None: print("  Contract example:\n"+indent(pretty(item["example"])))
    print("\n"+"-"*68)
    print("MVP STATUS: READY" if report["mvp_pass"] else "MVP STATUS: NOT READY")
    if report["mvp_pass"]: print("Shift Mode: python simulation/shift.py --shift 1")
    print("VISIBLE CHECKS: ALL PASS" if report["visible_pass"] else "VISIBLE CHECKS: WORK REMAINS")


def main():
    parser=argparse.ArgumentParser(description="Check currently unlocked Kitchen Rush contracts.")
    parser.add_argument("--json",action="store_true"); parser.add_argument("--stage",type=int,choices=range(1,9)); parser.add_argument("--all",action="store_true",help=argparse.SUPPRESS)
    args=parser.parse_args(); report=run_checks(args.stage,args.all and os.environ.get("KITCHEN_RUSH_DEV_MODE")=="1")
    print(json.dumps(report,indent=2,default=str)) if args.json else print_report(report)
    raise SystemExit(0 if report["visible_pass"] else 1)


if __name__=="__main__": main()
