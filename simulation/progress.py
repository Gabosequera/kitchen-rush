"""Local progress state used by the checker and shift simulator."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".kitchen_rush"
STATE_FILE = STATE_DIR / "progress.json"

DEFAULT_STATE = {
    "unlocked_stage": 4,
    "completed_shifts": [],
    "revealed_checks": [],
    "last_seed": None,
}


def load_progress():
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_STATE)
    return {**DEFAULT_STATE, **data}


def save_progress(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def reset_progress():
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    return dict(DEFAULT_STATE)


def unlock_stage(stage):
    state = load_progress()
    state["unlocked_stage"] = max(int(state.get("unlocked_stage", 4)), int(stage))
    save_progress(state)
    return state


def reveal_check(check_id):
    state = load_progress()
    checks = list(state.get("revealed_checks", []))
    if check_id not in checks:
        checks.append(check_id)
    state["revealed_checks"] = checks
    save_progress(state)
    return state


def complete_shift(shift_number, seed):
    state = load_progress()
    completed = set(state.get("completed_shifts", []))
    completed.add(int(shift_number))
    state["completed_shifts"] = sorted(completed)
    state["last_seed"] = int(seed)
    save_progress(state)
    return state
