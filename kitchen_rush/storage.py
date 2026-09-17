"""Persistence helpers unlocked by a later shift."""


def save_state(path, state):
    """Persist a JSON-compatible state dictionary and return True on success."""
    # Deliberate future bug: repr() is not a safe persistence format for this contract.
    with open(path, "w", encoding="utf-8") as file:
        file.write(repr(state))
    return True


def load_state(path):
    """Load and return persisted state, or None when no state exists."""
    # TODO: Future requirement.
    pass
