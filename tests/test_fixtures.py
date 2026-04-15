"""Validate every golden fixture against its corresponding schema."""

import json
from pathlib import Path

import pytest

from personal_event_mesh.validate import validate

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

# Map fixture directories to schema names
FIXTURE_SCHEMA_MAP = {
    "ha-automation": "ha-automation",
    "monitoring-event": "monitoring-event",
    "text-event": "text-event",
    "roadmap-event": "roadmap-event",
    "deploy-event": "deploy-event",
    "deal-alert": "deal-alert",
    "capability-report": "capability-report",
}


def _collect_fixtures() -> list[tuple[str, str]]:
    """Collect all fixture files with their expected schema name."""
    fixtures = []
    for dir_name, schema_name in FIXTURE_SCHEMA_MAP.items():
        fixture_dir = FIXTURES_DIR / dir_name
        if fixture_dir.exists():
            for f in sorted(fixture_dir.glob("*.json")):
                fixtures.append((str(f), schema_name))
    return fixtures


@pytest.mark.parametrize(
    "fixture_path,schema_name",
    _collect_fixtures(),
    ids=lambda x: Path(x).name if "/" in str(x) else x,
)
def test_fixture_matches_schema(fixture_path: str, schema_name: str):
    with open(fixture_path) as f:
        event = json.load(f)
    errors = validate(event, schema_name)
    assert errors == [], f"Fixture {fixture_path} failed validation:\n" + "\n".join(
        f"  - {e}" for e in errors
    )
