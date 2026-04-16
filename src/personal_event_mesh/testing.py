"""Test helpers for consumer repos."""

from __future__ import annotations

import json
from pathlib import Path

from personal_event_mesh.validate import validate

# Fixtures ship inside the package
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(fixture_path: str) -> dict:
    """Load a golden test fixture by relative path.

    Example: load_fixture("monitoring-event/uptime-kuma-down.json")
    """
    path = FIXTURES_DIR / fixture_path
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path} (looked at {path})")
    return json.loads(path.read_text())


def assert_contract_compatible(event: dict, schema_name: str) -> None:
    """Assert that an event validates against its schema.

    Raises AssertionError with details on failure. Use in pytest tests.
    """
    errors = validate(event, schema_name)
    if errors:
        raise AssertionError(
            f"Contract violation for schema '{schema_name}':\n"
            + "\n".join(f"  - {e}" for e in errors)
        )


class MockStream:
    """Phase 2 stub. Records published events for Redis-free unit testing.

    When Phase 2 ships, this will be backed by a real Redis mock.
    For now it just records events in memory for test assertions.
    """

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def publish(self, stream_name: str, event: dict) -> None:
        self.events.append((stream_name, event))

    def get_events(self, stream_name: str | None = None) -> list[dict]:
        if stream_name:
            return [e for s, e in self.events if s == stream_name]
        return [e for _, e in self.events]

    def clear(self) -> None:
        self.events.clear()
