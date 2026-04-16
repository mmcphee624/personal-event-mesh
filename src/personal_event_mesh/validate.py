"""Schema loading and event validation."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

# Schemas ship inside the package
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"


@lru_cache(maxsize=32)
def _load_schema(schema_name: str) -> dict:
    """Load a schema by name. Supports nested paths like 'monitoring-event/uptime-kuma'."""
    path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name} (looked at {path})")
    return json.loads(path.read_text())


def _build_registry() -> Registry:
    """Build a referencing Registry with all schemas for $ref resolution."""
    resources: list[tuple[str, Resource]] = []
    for schema_path in SCHEMAS_DIR.rglob("*.schema.json"):
        schema = json.loads(schema_path.read_text())
        schema_id = schema.get("$id")
        if schema_id:
            resources.append((schema_id, Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def _get_validator(schema_name: str) -> Draft202012Validator:
    """Create a validator for a named schema with full $ref resolution."""
    schema = _load_schema(schema_name)
    registry = _build_registry()
    return Draft202012Validator(schema, registry=registry)


def validate(event: dict, schema_name: str) -> list[str]:
    """Validate event dict against a named schema.

    Returns a list of error messages. Empty list means the event is valid.
    """
    validator = _get_validator(schema_name)
    return [err.message for err in validator.iter_errors(event)]


def validate_or_raise(event: dict, schema_name: str) -> None:
    """Validate event dict against a named schema.

    Raises ValidationError on the first validation error.
    """
    validator = _get_validator(schema_name)
    validator.validate(event)
