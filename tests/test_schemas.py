"""Validate that all schema files are valid JSON Schema Draft 2020-12."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _collect_schemas() -> list[Path]:
    return sorted(SCHEMAS_DIR.rglob("*.schema.json"))


@pytest.mark.parametrize(
    "schema_path",
    _collect_schemas(),
    ids=lambda p: str(p.relative_to(SCHEMAS_DIR)),
)
def test_schema_is_valid(schema_path: Path):
    schema = json.loads(schema_path.read_text())
    # check_schema raises SchemaError if the schema itself is invalid
    Draft202012Validator.check_schema(schema)


def test_all_schemas_have_description():
    """Every schema should have a description field for documentation."""
    for schema_path in _collect_schemas():
        schema = json.loads(schema_path.read_text())
        # Skip _meta.schema.json (it's a definitions file)
        if schema_path.name == "_meta.schema.json":
            continue
        # Skip the union schema (ingest-event)
        if "oneOf" in schema:
            continue
        assert "description" in schema, f"{schema_path.name} missing description"
